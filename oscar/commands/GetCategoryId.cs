using Discord.Commands;
using oscar;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace oscar.Commands
{
    public class GetCategoryId : ModuleBase<SocketCommandContext>
    {
        [Command("categoryid"), Summary("Gets a game id")]
        public async Task GetId([Remainder] string input)
        {
            try
            {
                var index = input.IndexOf(' ');
                var gameId = input.Substring(0, index);
                var category = input.Substring(index + 1);
                var game = SpeedrunBot.Client.Games.GetGame(gameId);
                var id = game.Categories.FirstOrDefault(x => string.Equals(x.Name, category, StringComparison.OrdinalIgnoreCase)).ID;
                await Context.Channel.SendMessageAsync(id);
            }
            catch (Exception)
            {
                await Context.Channel.SendMessageAsync("Could not find any category, either none exist or an error occurred.");
            }
        }
    }
}