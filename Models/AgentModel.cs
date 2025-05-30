using System.IO;
using System.Windows.Media.Imaging;

namespace AgentApp.Models
{
    public class AgentModel
    {
        public int ID { get; set; }
        public string Title { get; set; }
        public string AgentType { get; set; }
        public string Phone { get; set; }
        public string Email { get; set; }
        public string Logo { get; set; }
        public int Priority { get; set; }
        public int SalesCount { get; set; }
        public double Discount { get; set; }
        public BitmapImage DisplayImage
        {
            get
            {
                string path = (string.IsNullOrWhiteSpace(Logo) || Logo.ToLower() == "нет")
                    ? @"pack://application:,,,/Assets/default.png"
                    : Path.GetFullPath(Logo.TrimStart('\\', '/'));

                try
                {
                    return new BitmapImage(new Uri(path, UriKind.Absolute));
                }
                catch
                {
                    return new BitmapImage(new Uri(@"pack://application:,,,/Assets/default.png"));
                }
            }
        }
    }
}
