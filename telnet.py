import asyncio
import logging
from typing import Optional

class ModernTCPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False

    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
            logging.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            return False

    async def read_data(self) -> Optional[str]:
        if not self.connected or not self.reader:
            return None
        try:
            data = await self.reader.read(100)
            return data.decode() if data else None
        except Exception as e:
            logging.error(f"Read error: {e}")
            return None

    async def write_data(self, data: str) -> bool:
        if not self.connected or not self.writer:
            return False
        try:
            self.writer.write(data.encode())
            await self.writer.drain()
            return True
        except Exception as e:
            logging.error(f"Write error: {e}")
            return False

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        logging.info("Connection closed")

async def main():
    logging.basicConfig(level=logging.INFO)
    client = ModernTCPClient('192.168.1.7', 23)
    
    try:
        if await client.connect():
            while True:
                data = await client.read_data()
                if data:
                    logging.info(f"Received: {data}")
                
                # await client.write_data("Hello ESP32")
                await asyncio.sleep(0)
                
    except KeyboardInterrupt:
        logging.info("Closing connection...")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())