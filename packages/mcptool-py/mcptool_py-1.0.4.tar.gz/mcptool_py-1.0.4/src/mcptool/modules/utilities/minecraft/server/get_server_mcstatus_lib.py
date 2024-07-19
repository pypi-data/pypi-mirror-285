import socket
import dns
import re

from mcstatus import JavaServer, BedrockServer
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from typing import Union
from loguru import logger


from ..bot.server_response import BotServerResponse
from ..bot.utilities import BotUtilities
from . import JavaServerData, BedrockServerData, clean_output


class MCServerData:
    def __init__(self, target: str, bot: bool = True) -> None:
        self.target = target
        self.bot = bot
        self.ip_address: Union[str, None] = None
        self.port: Union[int, None] = None

    @logger.catch
    def get(self) -> Union[JavaServerData, BedrockServerData, None]:
        """
        Method to get the server data from the server class.

        Returns:
            Union[JavaServerData, BedrockServerData, None]: The server data if the server is online, otherwise None
        """

        # mc.universocraft.com:25565
        self._get_server_address_and_port()

        # If the IP address is not valid, return None
        if self.ip_address is None:
            return None

        # If the port is not valid, return None
        if isinstance(self.port, int) and (self.port < 0 or self.port > 65535):
            return None

        # Try to get the data from the Java server class
        data: Union[JavaServerData, BedrockServerData, None] = self._get_data(JavaServer(host=self.ip_address, port=self.port))

        # If the data is still None, try to get the data from the Bedrock server class
        if data is None:
            self.port = 19132
            data = self._get_data(BedrockServer(host=self.ip_address, port=self.port))

        # If the data is still None, return None
        if data is None:
            return None

        return data

    @logger.catch
    def _get_data(self, function: Union[JavaServer, BedrockServer]) -> Union[JavaServerData, BedrockServerData, None]:
        """
        Method to get the server data from the server class.

        Args:
            function (Union[JavaServer, BedrockServer]): The server class to get the data from

        Returns:
            dict: The server data if the server is online, otherwise None
        """

        try:
            data: Union[JavaStatusResponse, BedrockStatusResponse, None] = function.status()

            if data is None:
                return None

            if isinstance(data, JavaStatusResponse):
                player_list: Union[list, str] = []
                players: Union[str, None] = data.players.sample

                # Get the players
                if hasattr(data.players, 'sample') and data.players.sample is not None:
                    player_list = [{'name': player.name, 'id': player.id} for player in data.players.sample]

                if len(player_list) > 0:
                    players = MCServerData._get_players(player_list)
                    players: str = ', '.join(players)

                # Get the mod info
                mod_info = data.raw.get('modinfo', {})
                mod_type: str = mod_info.get('type', None) if isinstance(mod_info, dict) else None
                mod_list: Union[list, str] = mod_info.get('modList', []) if isinstance(mod_info, dict) else []

                if len(mod_list) > 0:
                    mod_list: list = [f'&f&l{mod["modid"]} &8&l(&a&l{mod["version"]}&8&l)' for mod in mod_list]
                    mod_list: str = ', '.join(mod_list)

                else:
                    mod_list: str = 'No mods found'

                if self.bot:
                    if ':' in self.target:
                        bot_output: str = clean_output(BotServerResponse(self.ip_address, self.port, data.version.protocol).get_response())

                    else:
                        bot_output: str = clean_output(BotServerResponse(self.target, 25565, data.version.protocol).get_response())

                    # Get the bot color response
                    bot_output = BotUtilities.get_bot_color_response(bot_output)

                else:
                    bot_output: str = ''

                return JavaServerData(
                    ip_address=str(self.ip_address),
                    port=int(self.port),
                    motd=clean_output(data.description),
                    original_motd=data.description,
                    version=clean_output(data.version.name),
                    original_version=data.version.name,
                    protocol=str(data.version.protocol),
                    connected_players=str(data.players.online),
                    max_players=str(data.players.max),
                    players=players,
                    player_list=player_list,
                    mod=mod_type,
                    mods=mod_list,
                    favicon=data.favicon,
                    ping=int(data.latency),
                    bot_output=bot_output
                )

            if isinstance(data, BedrockStatusResponse):
                bot_output: str = '&c&lIncompatible'

                return BedrockServerData(
                    ip_address=str(self.ip_address),
                    port=int(self.port),
                    motd=clean_output(data.description),
                    version=clean_output(data.version.name),
                    protocol=str(data.version.protocol),
                    connected_players=str(data.players.online),
                    max_players=str(data.players.max),
                    brand=data.version.brand,
                    map=clean_output(data.map),
                    gamemode=clean_output(data.gamemode),
                    ping=int(data.latency),
                    bot_output=bot_output
                )

        except (ConnectionRefusedError, TimeoutError, OSError, socket.gaierror):
            return None

    @logger.catch
    def _get_server_address_and_port(self) -> None:
        """
        Method to get the server address and port
        """

        # Check if the target has a port
        # Format: mc.server.com:25565 or 127.0.0.1:25565
        if ':' in self.target:
            target_data: list = self.target.split(':')
            self.ip_address = target_data[0]
            self.port = int(target_data[1])

        # If the target does not have a port
        # Format: mc.server.com or 127.0.0.1
        else:
            self.ip_address = self.target
            self._resolve_port()

        # Resolve the IP address
        # If the IP address is not numeric
        self._resolve_ip()

    @logger.catch
    def _resolve_ip(self) -> None:
        """
        Method to resolve the IP address of the server
        """

        # If the IP address is not valid
        if self.ip_address is None:
            return

        # If the IP address is a domain
        if not self.ip_address.isnumeric():
            try:
                self.ip_address = socket.gethostbyname(self.ip_address)

            except (socket.gaierror, OSError, UnicodeError):
                self.ip_address = None

    @logger.catch
    def _resolve_port(self) -> None:
        """
        Method to resolve the port of the server
        using the SRV DNS record.
        """

        # Construct the SRV DNS query hostname using the Minecraft format.
        hostname: str = f'_minecraft._tcp.{self.ip_address}'

        try:
            # Use the dns.resolver to query SRV DNS records for the server.
            answers = dns.resolver.resolve(hostname, 'SRV')

            # Extract the target port information from the SRV DNS record.
            self.port = answers[0].port

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout, dns.name.EmptyLabel):
            self.port = 25565

    @logger.catch
    @staticmethod
    def _get_players(players: Union[list, None]) -> list:
        """
        Method to get the players from the player list

        Args:
            players (Union[list, None]): The player list

        Returns:
            list: The list of players
        """

        return [player['name'] for player in players] if players is not None else []
