using Discord;
using Discord.Commands;
using Discord.WebSocket;
using oscar.Database;
using System;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;

namespace oscar
{
    public class DiscordBot
    {
        private static DiscordSocketClient client;
        private static CommandService commandService;
        private const char commandPrefix = '!';
        private const LogSeverity logSeverity = LogSeverity.Info;
        private const ulong botMaintainerId = 124860286774673408;

        public DiscordBot(string token)
        {
            InitializeClient();
            InitializeCommandService();
            StartAsync(token).GetAwaiter().GetResult();
        }

        public async Task SendEmbed(ulong guildId, ulong channelId, Embed embed)
        {
            await client.GetGuild(guildId).GetTextChannel(channelId).SendMessageAsync("", false, embed);
        }

        private async Task StartAsync(string token)
        {
            await client.LoginAsync(TokenType.Bot, token);
            await client.StartAsync();
        }

        private static void InitializeClient(LogSeverity logSeverity = LogSeverity.Info)
        {
            var discordSocketConfig = new DiscordSocketConfig
            {
                LogLevel = logSeverity
            };
            client = new DiscordSocketClient();
            client.MessageReceived += Client_MessageReceived_Async;
            client.Log += Client_Log_Async;
        }

        private static void InitializeCommandService(LogSeverity logSeverity = LogSeverity.Info)
        {
            var commandServiceConfig = new CommandServiceConfig
            {
                CaseSensitiveCommands = true,
                DefaultRunMode = RunMode.Async,
                LogLevel = logSeverity
            };
            commandService = new CommandService(commandServiceConfig);
            commandService.AddModulesAsync(Assembly.GetEntryAssembly(), null).GetAwaiter().GetResult();
        }

        private static async Task Client_Log_Async(LogMessage arg)
        {
            await Task.Run(() => Console.WriteLine($"{arg.Source}: {arg.Message}"));
            return;
        }

        private static async Task Client_MessageReceived_Async(SocketMessage arg)
        {
            var message = arg as SocketUserMessage;
            var argPos = 0;

            if (IsAuthorizedUser(message.Author.Id) && message.HasCharPrefix(commandPrefix, ref argPos))
            {
                var context = new SocketCommandContext(client, message);
                var result = await commandService.ExecuteAsync(context, argPos, null);
                if (!result.IsSuccess)
                {
                    Console.WriteLine($"Command {context.Message.Content} resulted in error {result.ErrorReason}");
                }
            }
        }

        private static bool IsAuthorizedUser(ulong userId)
        {
            if (userId == botMaintainerId)
            {
                return true;
            }
            else if (userId == client.CurrentUser.Id)
            {
                return false;
            }
            else
            {
                using (var dbContext = new DatabaseContext())
                {
                    return dbContext.AuthorizedUsers.Any(x => x.UserId == userId);
                }
            }
        }
    }
}
