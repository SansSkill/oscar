using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace Oscar
{
    class Program
    {
        private static DiscordBot discordBot;
        private static readonly string projectDirectory = @"C:\Users\Gebruiker\source\repos\oscar\oscar";

        static void Main(string[] args)
        {
#if DEBUG
            var token = File.ReadAllText(Path.Combine(projectDirectory, @"Data\token"));
#else
            var token = args[0];
#endif
            discordBot = new DiscordBot(token);

            Task.Delay(-1).GetAwaiter().GetResult();
        }
    }
}