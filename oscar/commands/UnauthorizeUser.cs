using Discord.Commands;
using oscar.Database;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace oscar.Commands
{
    public class UnauthorizeUser : ModuleBase<SocketCommandContext>
    {
        [Command("Unauthorize"), Summary("Unauthorizes a user")]
        public async Task Unauthorize([Remainder] string userIdString)
        {
            try
            {
                var userId = ulong.Parse(userIdString);
                using (var dbContext = new DatabaseContext())
                {
                    if (dbContext.AuthorizedUsers.Where(x => x.UserId == userId).Count() == 0)
                    {
                        await Context.Channel.SendMessageAsync($"User was not authorized!");
                    }
                    else
                    {
                        dbContext.AuthorizedUsers.Remove(new AuthorizedUser
                        {
                            UserId = userId
                        });
                        await Context.Channel.SendMessageAsync($"Unauthorized the user!");
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
