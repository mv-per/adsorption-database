from invoke import task


@task
def test(ctx):
    ctx.run("pytest --cov-report term-missing --cov")
