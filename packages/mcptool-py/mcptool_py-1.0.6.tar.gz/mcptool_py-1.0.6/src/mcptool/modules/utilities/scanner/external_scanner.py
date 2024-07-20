import subprocess
import threading
import re

from loguru import logger
from typing import Union
from mccolors import mcwrite
from easyjsonpy import get_config_value

from ..minecraft.server import JavaServerData, BedrockServerData
from ..minecraft.server.get_server import ServerData
from ..minecraft.server.show_server import ShowMinecraftServer
from ..managers.language_utils import LanguageUtils as LM
from ..path.mcptool_path import MCPToolPath
from ..constants import OS_NAME, BUUNGE_EXPLOIT_VULNERABLE_MESSAGE


class ExternalScanner:
    def __init__(self, target: str, port_range: str, scanner: str) -> None:
        self.target: str = target
        self.port_range: str = port_range
        self.scanner: str = scanner
        self.first_line: bool = True
        self.command_output: str = ''
        self.show_output: bool = get_config_value('scannerOptions.showScanOutput')
        self.output: dict = {
            "open_ports": {
                "other": [],
                "minecraft": [],
                "bungeeExploitVulnerable": [],
                "count": 0
            }
        }
        self.stopped: bool = False
        self.threads: list = []
        self.semaphore = threading.Semaphore(15)

    @logger.catch
    def scan(self) -> Union[dict, None]:
        """
        Scan the target for open ports.

        Returns:
            Union[dict, None]: The open ports found.
        """

        command: str = self._get_command()

        if command is None:
            logger.warning(f'Cannot scan target. Invalid command. {command}')
            return None

        text_to_search, pattern, invalid_ip_text, invalid_ports_text = self._get_scan_params()

        if text_to_search == '':
            logger.warning(f'Cannot scan target. Invalid scan parameters. {text_to_search}')
            return None

        try:
            process: subprocess.Popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

            # Review each line of the process output.
            for line in process.stdout:
                output_line: str = line.decode('latin-1').strip()
                self.command_output += output_line

                if self.first_line:
                    if self.scanner == 'qubo':
                        # Java not installed.
                        if 'not found' in output_line or '"java"' in output_line:
                            logger.warning('Cannot scan target. Java is not installed.')
                            mcwrite(LM.get('errors.javaNotInstalled'))
                            self.stopped = True
                            return None

                        # Qubo.jar not found.
                        if 'qubo.jar' in output_line:
                            logger.warning('Cannot scan target. Qubo.jar not found.')
                            mcwrite(LM.get('errors.quboJarNotFound'))
                            self.stopped = True
                            return None

                    self.first_line = False

                if self.show_output:
                    print(output_line)

                # If the line that refers to the IP entered as invalid.
                if any(text in output_line for text in invalid_ip_text):
                    logger.warning(f'Invalid IP address: {self.target}. Cannot scan target.')
                    mcwrite(LM.get('errors.invalidIpRange'))
                    self.stopped = True
                    return None

                # If the line that refers to the port range not being valid.
                if any(text in output_line for text in invalid_ports_text):
                    logger.warning(f'Invalid port range: {self.port_range}. Cannot scan target.')
                    mcwrite(LM.get('errors.invalidPortRange'))
                    self.stopped = True
                    return None

                # If the line contains an ip and a port.
                if text_to_search in output_line:
                    server: Union[str, None] = self._extract_server_info(output_line=output_line, pattern=pattern)

                    if server is None:
                        continue

                    # Start a thread to get the server data and show it.
                    server_thread = threading.Thread(target=self.get_server_data, args=(server,))
                    server_thread.start()
                    self.threads.append(server_thread)

            process.wait()

            if process.returncode != 0:
                logger.warning(f'Cannot scan target. Error occurred. {process.returncode} Command output: {self.command_output}')
                return None

        except (KeyboardInterrupt, ValueError):
            self.stopped = True

            try:
                process.terminate()

            except UnboundLocalError:
                pass

        for thread in self.threads:
            thread.join()

        return self.output

    @logger.catch
    def _get_command(self) -> Union[str, None]:
        """
        Get the command to scan the target.

        Returns:
            Union[str, None]: The command to scan the target.
        """

        command: Union[str, None] = get_config_value(f'scannerOptions.externalScanners.{self.scanner}.command')

        if command is None:
            return None

        if self.scanner == 'qubo':
            path: str = MCPToolPath().get()
            qubo_jar_path: str = f'{path}/scanners'
            command = f'cd {qubo_jar_path} && {command}'

        if OS_NAME == 'windows':
            command = f'C: && {command}'

        command = command.replace('%target%', self.target).replace('%ports%', self.port_range)
        return command

    @logger.catch
    def _get_scan_params(self) -> tuple:
        """
        Get the scan parameters.

        Returns:
            tuple: The scan parameters.
        """

        scan_params = {
            'nmap': ('Discovered open port', r'open port (\d+)/\w+ on (\d+\.\d+\.\d+\.\d+)', ['Failed to resolve "'], ['Your port specifications are illegal.', 'Your port range']),
            'masscan': ('Discovered open port', r'open port (\d+)/\w+ on (\d+\.\d+\.\d+\.\d+)', ['ERROR: bad IP address/range:', 'unknown command-line parameter'], ['bad target port:']),
            'qubo': (')(', r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\b', ['Invalid IP range.'], ['port is out of range', 'For input string:'])
        }

        return scan_params.get(self.scanner, ('', '', [], []))

    @logger.catch
    def _extract_server_info(self, output_line: str, pattern: str) -> Union[str, None]:
        """
        Extract the server information from the output line.

        Args:
            output_line (str): The output line.
            pattern (str): The pattern to search for.
            scan_method (str): The scan method.

        Returns:
            str: The server information.
        """

        match: re.Match = re.search(pattern, output_line)

        if match:
            if self.scanner in ('nmap', 'masscan'):
                server: str = f'{match.group(2)}:{match.group(1)}'

            else:
                server: str = match.group(0)

            return server

        return None

    @logger.catch
    def get_server_data(self, server):
        """
        Get the server data and show it.

        Args:
            server (str): The server to get the data.
        """

        with self.semaphore:
            server_data: Union[JavaServerData, BedrockServerData, None] = ServerData(server).get_data()

            if self.stopped:
                return

            if server_data is not None:
                ShowMinecraftServer.show(server_data)

                if BUUNGE_EXPLOIT_VULNERABLE_MESSAGE in server_data.bot_output:
                    self.output['open_ports']['bungeeExploitVulnerable'].append(server)

                else:
                    self.output['open_ports']['minecraft'].append(server)

            else:
                self.output['open_ports']['other'].append(server)

            self.output['open_ports']['count'] += 1
