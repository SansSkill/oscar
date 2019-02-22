using System.ComponentModel.DataAnnotations.Schema;

namespace Oscar.Database
{
    public class TrackedTime
    {
        [ForeignKey("TrackedCategory")]
        public string CategoryId { get; set; }

        public string Runner { get; set; }

        public string Time { get; set; }
    }
}
