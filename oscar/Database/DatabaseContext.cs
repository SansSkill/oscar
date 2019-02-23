using Microsoft.EntityFrameworkCore;

namespace oscar.Database
{
    public class DatabaseContext : DbContext
    {
        public DbSet<TrackedLeaderboard> TrackedLeaderboards { get; set; }
        public DbSet<TrackedTime> TrackedTimes { get; set; }
        public DbSet<AuthorizedUser> AuthorizedUsers { get; set; }

        private const string dbLocation = @"C:\Users\Gebruiker\source\repos\oscar\oscar\Data\database.sqlite";

        protected override void OnConfiguring(DbContextOptionsBuilder options)
        {
            options.UseSqlite($"Data Source={dbLocation}");
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<TrackedTime>().HasKey(o => new { o.CategoryId, o.Runner });
            modelBuilder.Entity<TrackedLeaderboard>().HasKey(o => new { o.GameId, o.CategoryId });
        }
    }
}
