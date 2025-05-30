using System.Data;
using AgentApp.Models;

namespace AgentApp.Data
{
    public static class AgentRepository
    {
        public static List<AgentModel> GetAgents()
        {
            const string query = @"
                SELECT 
                    a.ID, a.Title, a.Phone, a.Email, a.Logo, a.Priority,
                    at.Title AS AgentType,
                    COALESCE(SUM(ps.ProductCount), 0) AS SalesCount,
                    COALESCE(SUM(ps.ProductCount * p.MinCostForAgent), 0) AS TotalSalesAmount
                FROM Agent a
                JOIN AgentType at ON at.ID = a.AgentTypeID
                LEFT JOIN ProductSale ps ON ps.AgentID = a.ID
                LEFT JOIN Product p ON p.ID = ps.ProductID
                GROUP BY a.ID";

            var table = DatabaseManager.ExecuteQuery(query);
            var agents = new List<AgentModel>();

            foreach (DataRow row in table.Rows)
            {
                var totalAmount = Convert.ToDouble(row["TotalSalesAmount"]);
                agents.Add(new AgentModel
                {
                    ID = Convert.ToInt32(row["ID"]),
                    Title = row["Title"].ToString(),
                    Phone = row["Phone"].ToString(),
                    Email = row["Email"].ToString(),
                    Logo = row["Logo"]?.ToString(),
                    AgentType = row["AgentType"].ToString(),
                    Priority = Convert.ToInt32(row["Priority"]),
                    SalesCount = Convert.ToInt32(row["SalesCount"]),
                    Discount = CalculateDiscount(totalAmount)
                });
            }

            return agents;
        }

        private static double CalculateDiscount(double totalSales)
        {
            return totalSales switch
            {
                < 10000 => 0,
                < 50000 => 5,
                < 150000 => 10,
                < 500000 => 20,
                _ => 25
            };
        }
    }
}
