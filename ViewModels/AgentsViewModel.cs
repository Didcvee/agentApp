using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;
using AgentApp.Data;
using AgentApp.Models;

namespace AgentApp.ViewModels
{
    public class AgentsViewModel : INotifyPropertyChanged
    {
        private const int PageSize = 10;

        private ObservableCollection<AgentModel> _allAgents;
        private ObservableCollection<AgentModel> _displayedAgents;
        private int _currentPage = 1;
        private string _searchText = "";
        private string _selectedType = "Все типы";
        private string _selectedSort = "Наименование ↑";

        public ObservableCollection<AgentModel> DisplayedAgents
        {
            get => _displayedAgents;
            set { _displayedAgents = value; OnPropertyChanged(); }
        }

        public int CurrentPage
        {
            get => _currentPage;
            set { _currentPage = value; UpdateDisplayedAgents(); OnPropertyChanged(); }
        }

        public int PageCount => (int)Math.Ceiling((double)FilteredAgents.Count() / PageSize);

        public string SearchText
        {
            get => _searchText;
            set { _searchText = value; CurrentPage = 1; UpdateDisplayedAgents(); OnPropertyChanged(); }
        }

        public string SelectedType
        {
            get => _selectedType;
            set { _selectedType = value; CurrentPage = 1; UpdateDisplayedAgents(); OnPropertyChanged(); }
        }

        public string SelectedSort
        {
            get => _selectedSort;
            set { _selectedSort = value; CurrentPage = 1; UpdateDisplayedAgents(); OnPropertyChanged(); }
        }

        public ObservableCollection<string> AgentTypes { get; set; }
        public ObservableCollection<string> SortOptions { get; } = new ObservableCollection<string>
        {
            "Наименование ↑", "Наименование ↓",
            "Скидка ↑", "Скидка ↓",
            "Приоритет ↑", "Приоритет ↓"
        };

        public ICommand NextPageCommand { get; }
        public ICommand PrevPageCommand { get; }
        public ICommand GoToPageCommand { get; }

        public ObservableCollection<int> PageNumbers => new(Enumerable.Range(1, PageCount));

        public AgentsViewModel()
        {
            _allAgents = new ObservableCollection<AgentModel>(AgentRepository.GetAgents());
            AgentTypes = new ObservableCollection<string> { "Все типы" };
            foreach (var t in _allAgents.Select(a => a.AgentType).Distinct())
                AgentTypes.Add(t);

            NextPageCommand = new RelayCommand(_ => CurrentPage++, _ => CurrentPage < PageCount);
            PrevPageCommand = new RelayCommand(_ => CurrentPage--, _ => CurrentPage > 1);
            GoToPageCommand = new RelayCommand(p => CurrentPage = (int)p);

            UpdateDisplayedAgents();
        }

        private void UpdateDisplayedAgents()
        {
            var agents = FilteredAgents;

            agents = SelectedSort switch
            {
                "Наименование ↑" => agents.OrderBy(a => a.Title),
                "Наименование ↓" => agents.OrderByDescending(a => a.Title),
                "Скидка ↑" => agents.OrderBy(a => a.Discount),
                "Скидка ↓" => agents.OrderByDescending(a => a.Discount),
                "Приоритет ↑" => agents.OrderBy(a => a.Priority),
                "Приоритет ↓" => agents.OrderByDescending(a => a.Priority),
                _ => agents
            };

            DisplayedAgents = new ObservableCollection<AgentModel>(
                agents.Skip((CurrentPage - 1) * PageSize).Take(PageSize));

            OnPropertyChanged(nameof(PageNumbers));
        }

        private IEnumerable<AgentModel> FilteredAgents =>
            _allAgents.Where(a =>
                (SelectedType == "Все типы" || a.AgentType == SelectedType) &&
                (a.Title.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ||
                 a.Phone.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ||
                 a.Email.Contains(SearchText, StringComparison.OrdinalIgnoreCase))
            );

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged([CallerMemberName] string name = "") =>
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }
}
