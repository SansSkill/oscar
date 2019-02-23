using Discord.Commands;
using oscar.Database;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace oscar.Commands
{
    public class AuthorizeUser : ModuleBase<SocketCommandContext>
    {
        [Command("authorize"), Summary("Authorizes a user")]
        public async Task Authorize([Remainder] string userIdString)
        {
            try
            {
                var userId = ulong.Parse(userIdString);
                using (var dbContext = new DatabaseContext())
                {
                    if (dbContext.AuthorizedUsers.Where(x => x.UserId == userId).Count() > 0)
                    {
                        await Context.Channel.SendMessageAsync($"User was already authorized!");
                    }
                    else
                    {
                        dbContext.AuthorizedUsers.Add(new AuthorizedUser
                        {
                            UserId = userId
                        });
                        await Context.Channel.SendMessageAsync($"Authorized the user!");
                    }
                    dbContext.SaveChanges();
                }
            }
            catch (Exception)
            {
                await Context.Channel.SendMessageAsync($"An error has occurred.");
            }
        }
    }
}
