"""Start websocket connection."""

import threading

import daemon as py_daemon
import rich_click as click

from oxpecker import WORK_DIR
from oxpecker.tunnel import tunnel
from oxpecker.utils import retry_if_network_error
from oxpecker.ws_oxpk import ws_conn


@click.command(help="Connect to the websocket server for bidirectional communication.")
@click.pass_context
@click.option(
    "--detach/--no-detach",
    is_flag=True,
    help="[Experimental] Connect and put the process in background.",
    default=False,
)
# Copied and pasted from tunnle.py.
@click.option("--local-host", default="localhost", show_default=True)
@click.option("--local-port", default=22, show_default=True)
@click.option(
    "--remote-proto", default="tcp", help="Remote protocol.", show_default=True
)
@click.option("--remote-host", default="", help="Remote host.", show_default=True)
@click.option("--remote-port", help="Remote port.", show_default=True)
@retry_if_network_error()
def serve(ctx, detach, local_host, local_port, remote_proto, remote_host, remote_port):
    """Connect to the websocket server."""
    insecure_skip_tls_verify = ctx.find_root().params["insecure_skip_tls_verify"]
    if detach:
        with py_daemon.DaemonContext(
                pidfile=(WORK_DIR / "serve.pid").open("w"),
                stdout=(WORK_DIR / "serve.out.log").open("w+"),
                stderr=(WORK_DIR / "serve.err.log").open("w+"),
        ) as dc:
            t = threading.Thread(
                target=ctx.invoke,
                args=(tunnel,),
                kwargs={
                    "local_host": local_host,
                    "local_port": local_port,
                    "remote_proto": remote_proto,
                    "remote_host": remote_host,
                    "remote_port": remote_port,
                },
            )
            ws_conn(insecure_skip_tls_verify)
            click.echo(f"{dc.pidfile} = ")
    else:
        t = threading.Thread(
            target=ctx.invoke,
            args=(tunnel,),
            kwargs={
                "local_host": local_host,
                "local_port": local_port,
                "remote_proto": remote_proto,
                "remote_host": remote_host,
                "remote_port": remote_port,
            },
        )
        t.start()
        ws_conn(insecure_skip_tls_verify)


if __name__ == "__main__":
    serve()  # pylint: disable=no-value-for-parameter
