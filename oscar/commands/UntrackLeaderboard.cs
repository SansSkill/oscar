using Discord.Commands;
using oscar.Database;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace oscar.Commands
{
    public class UntrackLeaderboard : ModuleBase<SocketCommandContext>
    {
        [Command("untrack"), Summary("Untracks a given leaderboard")]
        public async Task UntrackAsync([Remainder] string input)
        {
            try
            {
                var gameId = input.Split()[0];
                var categoryId = input.Split()[1];
                using (var dbContext = new DatabaseContext())
                {
                    if (dbContext.TrackedLeaderboards.Where(x => x.GameId == gameId && x.CategoryId == categoryId).Count() == 0)
                    {
                        await Context.Channel.SendMessageAsync($"Already wasn't tracking that leaderboard!");
                    }
                    else
                    {
                        dbContext.TrackedLeaderboards.Remove(new TrackedLeaderboard
                        {
                            GameId = gameId,
                            CategoryId = categoryId
                        });
                        await Context.Channel.SendMessageAsync($"No longer tracking the leaderboard!");
                    }
                    dbContext.SaveChanges();
                }
            }
            catch (Exception)
            {
                await Context.Channel.SendMessageAsync("An error has occurred.");
            }
            return;
        }
    }
}
