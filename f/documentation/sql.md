# SQL

- [SQL](#sql)
	- [Terminal commands](#terminal-commands)
	- [Queries](#queries)
	- [Updates](#updates)

- [Basics](.basics.md) | [Interactions](interactions.md) | [SQL](sql.md)

## Terminal commands

```
psql -U postgres
```

## Queries

```py
    @commands.command()
    async def query(ctx):
        query = "SELECT * FROM users WHERE id = $1;"

        # This returns a asyncpg.Record object, which is similar to a dict
        row = await psql.db.fetchrow(query, ctx.author.id)
        await ctx.send("{}: {}".format(row["id"], row["data"]))
```

## Updates

```py
    @commands.command()
    async def update(ctx, *, new_data: str):
        # Once the code exits the transaction block, changes made in the block are committed to the db

        connection = await bot.db.acquire()
        async with connection.transaction():
            query = "UPDATE users SET data = $1 WHERE id = $2"
            await bot.db.execute(query, new_data, ctx.author.id)
        await bot.db.release(connection)

        await ctx.send("NEW:\n{}: {}".format(ctx.author.id, new_data))
```