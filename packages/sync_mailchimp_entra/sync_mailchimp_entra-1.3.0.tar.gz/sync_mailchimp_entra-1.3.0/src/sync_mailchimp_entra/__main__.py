import sync_mailchimp_entra.scripts as scripts
import asyncio

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(scripts.main())
