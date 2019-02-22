using System.IO;
using System.Reflection;
using System.Threading.Tasks;

namespace oscar
{
    class Program
    {
        private static DiscordBot discordBot;
        static void Main(string[] args)
        {
#if DEBUG
            var projectDirectory = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
            var tokenFile = Path.Combine(projectDirectory, @"..\..\data\token");
            var token = File.ReadAllText(tokenFile);
#else
            var token = args[0];
#endif
            discordBot = new DiscordBot(token);

            Task.Delay(-1).GetAwaiter().GetResult();
        }
    }
}