using Discord;
using Discord.Commands;
using Discord.WebSocket;
using System;
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

        public DiscordBot(string token)
        {
            InitializeClient();
            InitializeCommandService();
            StartAsync(token).GetAwaiter().GetResult();
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

            if (message.Author != client.CurrentUser && message.HasCharPrefix(commandPrefix, ref argPos))
            {
                var context = new SocketCommandContext(client, message);
                var result = await commandService.ExecuteAsync(context, argPos, null);
                if (!result.IsSuccess)
                {
                    Console.WriteLine($"Command {context.Message.Content} resulted in error {result.ErrorReason}");
                }
            }
        }
    }
}
