using System.Data;
using MySql.Data.MySqlClient;

namespace AgentApp.Data
{
    public static class DatabaseManager
    {
        private const string ConnectionString = "server=localhost;" +
                                                "user=root;" +
                                                "password=2121;" +
                                                "database=agent_app;" +
                                                "charset=utf8;";

        public static DataTable ExecuteQuery(string query, Dictionary<string, object> parameters = null)
        {
            using var connection = new MySqlConnection(ConnectionString);
            using var command = new MySqlCommand(query, connection);
            if (parameters != null)
            {
                foreach (var param in parameters)
                {
                    command.Parameters.AddWithValue(param.Key, param.Value);
                }
            }

            var table = new DataTable();
            try
            {
                connection.Open();
                using var adapter = new MySqlDataAdapter(command);
                adapter.Fill(table);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Database error: " + ex.Message);
            }

            return table;
        }
    }
}