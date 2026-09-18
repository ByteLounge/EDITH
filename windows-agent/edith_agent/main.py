import argparse
import asyncio
import logging
import sys
import httpx
from PIL import Image, ImageDraw

from edith_agent.config.settings import agent_settings
from edith_agent.security.credentials import credentials_store
from edith_agent.capabilities.registry import CapabilityRegistry
from edith_agent.connection.ws_client import AgentWebSocketClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("edith.agent")


def create_tray_icon():
    """Generates a small modern EDITH tray icon image."""
    img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a blue/cyan circle with 'E'
    draw.ellipse((4, 4, 60, 60), fill=(14, 165, 233, 255), outline=(56, 189, 248, 255), width=3)
    return img


async def pair_flow(server_url: str):
    """Executes the interactive device pairing flow."""
    print("=========================================")
    print("       EDITH Windows Agent Pairing       ")
    print("=========================================")
    print(f"Server Target: {server_url}")
    print("Open the EDITH Android app (or web dashboard), go to Devices > Add Device,")
    print("and enter the 6-digit pairing code shown.")
    print("-----------------------------------------")

    pairing_code = input("Enter 6-digit Pairing Code: ").strip()
    if not pairing_code:
        print("Pairing cancelled: code cannot be empty.")
        return False

    device_id = input(f"Enter Device ID [{agent_settings.DEVICE_ID}]: ").strip() or agent_settings.DEVICE_ID
    device_name = input(f"Enter Device Name [{agent_settings.DEVICE_NAME}]: ").strip() or agent_settings.DEVICE_NAME

    capabilities = CapabilityRegistry.discover_capabilities()
    payload = {
        "pairing_code": pairing_code,
        "device_id": device_id,
        "device_name": device_name,
        "device_type": "computer",
        "platform": "windows",
        "capabilities": capabilities,
        "version": agent_settings.VERSION
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{server_url}/api/v1/devices/pair/claim", json=payload, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                token = data["device_token"]
                credentials_store.save_device_credentials(device_id, token)
                print("-----------------------------------------")
                print("SUCCESS: Device paired successfully with EDITH Core!")
                print(f"Device ID: {device_id}")
                print(f"Credentials saved to: {credentials_store.storage_path}")
                print("You can now run the agent with: python -m edith_agent.main")
                return True
            else:
                error_detail = res.json().get("detail", res.text)
                print(f"Pairing failed ({res.status_code}): {error_detail}")
                return False
    except Exception as e:
        print(f"Network error connecting to backend: {e}")
        return False


def run_tray(ws_client: AgentWebSocketClient, loop: asyncio.AbstractEventLoop):
    """Starts the system tray icon in a dedicated thread."""
    try:
        import pystray
        icon_image = create_tray_icon()

        def on_quit(icon, item):
            logger.info("Quitting from system tray...")
            ws_client.stop()
            icon.stop()
            loop.call_soon_threadsafe(loop.stop)

        menu = pystray.Menu(
            pystray.MenuItem("EDITH Windows Agent: Running", None, enabled=False),
            pystray.MenuItem(f"Device: {ws_client.device_id}", None, enabled=False),
            pystray.MenuItem("Quit EDITH", on_quit)
        )

        tray = pystray.Icon("EDITH", icon_image, "EDITH Windows Agent", menu)
        tray.run()
    except Exception as e:
        logger.warning(f"Could not initialize system tray ({e}). Running in console mode.")


def main():
    parser = argparse.ArgumentParser(description="EDITH Windows Agent")
    parser.add_argument("--pair", action="store_true", help="Pair this Windows laptop with EDITH Core")
    parser.add_argument("--test-caps", action="store_true", help="Display discovered hardware capabilities and exit")
    parser.add_argument("--server", type=str, default=agent_settings.SERVER_URL, help="EDITH Core server URL")
    parser.add_argument("--no-tray", action="store_true", help="Run in console mode without tray icon")

    args = parser.parse_args()

    if args.test_caps:
        print("Discovered capabilities on this system:")
        for cap in CapabilityRegistry.discover_capabilities():
            print(f"  - {cap}")
        return

    if args.pair:
        asyncio.run(pair_flow(args.server))
        return

    # Check credentials
    token = credentials_store.get_token()
    device_id = credentials_store.get_device_id()

    if not token:
        print("No device credentials found.")
        print("Please pair this agent first: python -m edith_agent.main --pair")
        sys.exit(1)

    logger.info(f"Starting EDITH Windows Agent for device '{device_id}'...")
    ws_client = AgentWebSocketClient(
        server_url=args.server,
        device_token=token,
        device_id=device_id
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start WebSocket client in event loop
    ws_task = loop.create_task(ws_client.start())

    # Try tray icon if not disabled
    if not args.no_tray:
        import threading
        tray_thread = threading.Thread(target=run_tray, args=(ws_client, loop), daemon=True)
        tray_thread.start()

    try:
        loop.run_until_complete(ws_task)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agent stopped by user.")
    finally:
        ws_client.stop()


if __name__ == "__main__":
    main()
