using System.ComponentModel.DataAnnotations;

namespace oscar.Database
{
    public class AuthorizedUser
    {
        [Key]
        public ulong UserId { get; set; }
    }
}
