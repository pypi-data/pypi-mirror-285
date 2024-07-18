import typer


app = typer.Typer()


# 不给help参数时下面被装饰函数的注释会出现在help
@app.callback(invoke_without_command=True, help="A simple CLI tool for GROMACS")
def callback(ctx: typer.Context):
    """
    Args:
        ctx (typer.Context): Typer上下文对象，包含命令行参数和其他上下文信息。
    Raises:
        typer.Exit: 当没有子命令被调用时，退出程序并显示帮助信息。
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()  # 我们希望程序显示帮助信息并立即退出，而不是继续执行其他代码


@app.command()
def shoot():
    """
    Shoot the portal gun
    """
    typer.echo("Shooting portal gun")


@app.command()
def load():
    """
    Load the portal gun
    """
    typer.echo("Loading portal gun")
