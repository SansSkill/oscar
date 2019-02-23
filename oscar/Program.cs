using Discord;
using oscar.Database;
using SpeedrunComSharp;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace oscar
{
    class Program
    {
        private static DiscordBot discordBot;
        private static readonly string projectDirectory = @"C:\Users\Gebruiker\source\repos\oscar\oscar";
        private const int delay = 3600 * 1000; // An hour in milliseconds
        private const ulong guildId = 544856261926191107;
        private const ulong channelId = 544856261926191122;

        static void Main(string[] args)
        {
#if DEBUG
            var token = File.ReadAllText(Path.Combine(projectDirectory, @"Data\token"));
#else
            var token = args[0];
#endif
            discordBot = new DiscordBot(token);

            while (true)
            {
                Update();
                Task.Delay(delay).GetAwaiter().GetResult();
            }
        }

        private static void Update()
        {
            using (var dbContext = new DatabaseContext())
            {
                foreach (var trackedLeaderboard in dbContext.TrackedLeaderboards)
                {
                    var gameId = trackedLeaderboard.GameId;
                    var categoryId = trackedLeaderboard.CategoryId;
                    var leaderboard = SpeedrunBot.Client.Leaderboards.GetLeaderboardForFullGameCategory(gameId, categoryId);
                    var tiedWR = leaderboard.Records.Count(x => x.Rank == 1) > 1;
                    foreach (var record in leaderboard.Records)
                    {
                        var recordStatus = UpdateRecord(dbContext, record);
                        if (recordStatus != RecordStatus.Unchanged)
                        {
                            SendUpdateAsync(record, recordStatus, tiedWR).GetAwaiter().GetResult();
                        }
                    }
                }
            }
        }

        private static RecordStatus UpdateRecord(DatabaseContext dbContext, Record record)
        {
            var runner = record.Player.Name;
            var time = record.Times.Primary.ToString();
            var entry = dbContext.TrackedTimes.FirstOrDefault(x => x.CategoryId == record.CategoryID && x.Runner == runner);
            var trackedTime = new TrackedTime
            {
                CategoryId = record.CategoryID,
                Runner = runner,
                Time = time
            };
            if (entry == null)
            {
                dbContext.TrackedTimes.Add(trackedTime);
                return record.Rank == 1 ? RecordStatus.WR : RecordStatus.PB;
            }
            else
            {
                var timeUnchanged = trackedTime.Time == time;
                trackedTime.Time = time;
                return timeUnchanged ? RecordStatus.Unchanged :
                    record.Rank == 1 ? RecordStatus.WR : RecordStatus.PB;
            }
        }

        private static async Task SendUpdateAsync(Record record, RecordStatus recordStatus, bool tiedWR)
        {
            var achieved = recordStatus == RecordStatus.WR && !tiedWR ? "achieved the World Record!"
                : recordStatus == RecordStatus.WR && tiedWR ? "tied World Record!" : "achieved a new Personal Best!";
            var firstLine = $"{record.Player.Name} has {achieved}";
            var secondLine = $"{record.Times.Primary.ToString()} in {record.Game.Name} {record.Category.Name}";
            var thirdLine = $"{record.WebLink.ToString()}";
            var embedBuilder = new EmbedBuilder();
            embedBuilder.WithDescription($"{firstLine}\n{secondLine}\n{thirdLine}");
            await discordBot.SendEmbed(guildId, channelId, embedBuilder.Build());
        }
    }
}