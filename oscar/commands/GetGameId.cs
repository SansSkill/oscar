using Discord.Commands;
using oscar;
using System;
using System.Threading.Tasks;

namespace oscar.Commands
{
    public class GetGameId : ModuleBase<SocketCommandContext>
    {
        [Command("gameid"), Summary("Gets a game id")]
        public async Task GetId([Remainder] string game)
        {
            try
            {
                await Context.Channel.SendMessageAsync(SpeedrunBot.Client.Games.SearchGame(game).ID);
            }
            catch (Exception)
            {
                await Context.Channel.SendMessageAsync("Could not find any game, either none exist or an error occurred.");
            }
        }
    }
}
