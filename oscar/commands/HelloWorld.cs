using Discord.Commands;
using System.Threading.Tasks;

namespace SansBot.Commands
{
    public class HelloWorld : ModuleBase<SocketCommandContext>
    {
        [Command("helloworld"), Alias("hw"), Summary("Bot posts the phrase 'Hello World!' in chat")]
        public async Task HelloWorldAsync()
        {
            await Context.Channel.SendMessageAsync("Hello World!");
            return;
        }
    }
}