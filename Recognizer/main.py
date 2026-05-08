from argparse import ArgumentParser

from recognizer.serial_sender import list_serial_ports, send_digit_sequence


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Hand gesture recognizer")
    parser.add_argument(
        "--camera-index",
        type=int,
        default=None,
        help="Camera index to use. If omitted, the app auto-detects an available camera.",
    )
    parser.add_argument(
        "--serial-port",
        type=str,
        default=None,
        help="Serial port connected to STM32, for example COM5.",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="Serial baudrate used to send digits to STM32.",
    )
    parser.add_argument(
        "--stable-frames",
        type=int,
        default=4,
        help="How many consecutive frames must confirm a digit before it is sent.",
    )
    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List available serial ports and exit.",
    )
    parser.add_argument(
        "--send-test",
        nargs="?",
        const="12345",
        default=None,
        help="Send a digit sequence to STM32 and exit. Default sequence is 12345.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    try:
        if args.list_ports:
            ports = list_serial_ports()
            if ports:
                for port in ports:
                    print(port)
            else:
                print("No serial ports found.")
            return

        if args.send_test is not None:
            if args.serial_port is None:
                raise ValueError("--send-test requires --serial-port COMx")

            sent_digits = send_digit_sequence(
                port=args.serial_port,
                digits=args.send_test,
                baudrate=args.baudrate,
            )
            sent_text = "".join(str(digit) for digit in sent_digits)
            print(f"Sent {sent_text} to {args.serial_port} at {args.baudrate} baud.")
            return

        if args.serial_port is None:
            print("Serial disabled. Add --serial-port COMx to send digits to STM32.")
        else:
            print(f"Sending stable digits to {args.serial_port} at {args.baudrate} baud.")

        from recognizer.apps import run_finger_counter

        run_finger_counter(
            camera_index=args.camera_index,
            serial_port=args.serial_port,
            serial_baudrate=args.baudrate,
            stable_frames=args.stable_frames,
        )
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
