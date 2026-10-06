import socket
import re
from colorama import init, Fore, Style
import logging


logging.basicConfig(filename="syslog.txt", level=logging.INFO, format="%(asctime)s %(message)s")

def colorize_message(message):
    # Tijdstip geel maken
    timestamp_pattern = r"([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\.\d+)"
    message = re.sub(
        timestamp_pattern,
        lambda m: f"{Fore.YELLOW}{m.group(1)}{Style.RESET_ALL}",
        message,
    )

    # Alle IPv4 adressen paars maken
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    message = re.sub(
        ip_pattern,
        lambda m: f"{Fore.MAGENTA}{m.group(0)}{Style.RESET_ALL}",
        message,
    )

    return message


def Syslog_server():
    init()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 514))

    print(Fore.GREEN + "Syslog server gestart" + Style.RESET_ALL)

    RULES = {
        r"LINK-\d-UPDOWN": Fore.RED,
        r"LINEPROTO-\d-UPDOWN": Fore.YELLOW,
        r"CONFIG_I": Fore.CYAN,
        r"LOGGINGHOST_STARTSTOP": Fore.GREEN,
        r"AUTH_FAIL|LOGIN_FAIL|DENIED|FAILED": Fore.LIGHTRED_EX,
    }

    try:
        while True:
            try:
                data, addr = sock.recvfrom(65535)
            except socket.timeout:
                continue

            message = data.decode("utf-8", errors="ignore")

            logging.info("%s: %s", addr[0], message)

            color = Fore.WHITE

            for pattern, rule_color in RULES.items():
                if re.search(pattern, message):
                    color = rule_color
                    break

            message = colorize_message(message)

            print(
                f"{Fore.MAGENTA}{addr[0]}{Style.RESET_ALL}: "
                f"{color}{message}{Style.RESET_ALL}"
            )

    except KeyboardInterrupt:
        print("\nServer gestopt")

    finally:
        sock.close()


if __name__ == "__main__":
    Syslog_server()
