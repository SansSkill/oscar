using Discord.Commands;
using oscar.Database;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace oscar.Commands
{
    public class TrackLeaderboard : ModuleBase<SocketCommandContext>
    {
        [Command("track"), Summary("Tracks a given leaderboard")]
        public async Task TrackAsync([Remainder] string input)
        {
            try
            {
                var gameId = input.Split()[0];
                var categoryId = input.Split()[1];
                using (var dbContext = new DatabaseContext())
                {
                    if (dbContext.TrackedLeaderboards.Where(x => x.GameId == gameId && x.CategoryId == categoryId).Count() > 0)
                    {
                        await Context.Channel.SendMessageAsync($"Already tracking this leaderboard!");
                    }
                    else
                    {
                        dbContext.TrackedLeaderboards.Add(new TrackedLeaderboard
                        {
                            GameId = gameId,
                            CategoryId = categoryId
                        });
                        InitializeLeaderboard(dbContext, gameId, categoryId);
                        await Context.Channel.SendMessageAsync($"Now tracking the leaderboard!");
                    }
                    dbContext.SaveChanges();
                }
            }
            catch (Exception)
            {
                await Context.Channel.SendMessageAsync("An error has occurred");
            }
            return;
        }

        private void InitializeLeaderboard(DatabaseContext dbContext, string gameId, string categoryId)
        {
            var leaderboard = SpeedrunBot.Client.Leaderboards.GetLeaderboardForFullGameCategory(gameId, categoryId);

            foreach (var record in leaderboard.Records)
            {
                var runner = record.Player.Name;
                var time = record.Times.Primary.ToString();
                var entity = dbContext.TrackedTimes.FirstOrDefault(tt => tt.CategoryId == categoryId && tt.Runner == runner);
                if (entity == null)
                {
                    dbContext.TrackedTimes.Add(new TrackedTime
                    {
                        CategoryId = categoryId,
                        Runner = runner,
                        Time = time
                    });
                }
                else
                {
                    entity.Time = time;
                }
            }
        }
    }
}
