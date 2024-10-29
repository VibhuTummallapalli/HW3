from flask import Flask, render_template, request
import psycopg2
from psycopg2 import Error

app = Flask(__name__)

# Database connection utility functions
def connect_to_db(username='raywu1990', password='test', host='127.0.0.1', port='5432', database='dvdrental'):
    try:
        connection = psycopg2.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()
        return cursor, connection
    except (Exception, Error) as error:
        return None, str(error)

def disconnect_from_db(connection, cursor):
    if cursor:
        cursor.close()
    if connection:
        connection.close()

def execute_sql(cursor, sql, values=None):
    try:
        if values:
            cursor.execute(sql, values)
        else:
            cursor.execute(sql)

        # If it's a SELECT statement, return fetched results
        if sql.strip().upper().startswith("SELECT"):
            return cursor.fetchall(), None  # Return results and no error
        else:
            return None, None  # No results for non-SELECT queries
    except (Exception, Error) as error:
        return None, str(error)


# Route to insert a row into basket_a
@app.route('/api/update_basket_a')
def update_basket_a():
    cursor, connection = connect_to_db()
    if not cursor:
        return f"Error connecting to database: {connection}"

    # Update the SQL to use 'a' and 'fruit_a'
    sql = "INSERT INTO basket_a (a, fruit_a) VALUES (%s, %s)"
    values = (5, 'Cherry')  # Adjust as necessary for your use case

    _, error = execute_sql(cursor, sql, values)
    if error:
        return f"Error executing SQL: {error}"
    
    connection.commit()  # Commit the transaction
    disconnect_from_db(connection, cursor)
    return "Success!"

# Route to display unique fruits from basket_a and basket_b
@app.route('/api/unique')
def unique_fruits():
    cursor, connection = connect_to_db()
    if not cursor:
        return f"Error connecting to database: {connection}"

    # Get unique fruits in basket_a that are not in basket_b
    sql_a = """
    SELECT DISTINCT fruit_a FROM basket_a
    WHERE fruit_a NOT IN (SELECT fruit_b FROM basket_b);
    """

    # Get unique fruits in basket_b that are not in basket_a
    sql_b = """
    SELECT DISTINCT fruit_b FROM basket_b
    WHERE fruit_b NOT IN (SELECT fruit_a FROM basket_a);
    """

    result_a, error_a = execute_sql(cursor, sql_a)
    if error_a:
        return f"Error executing SQL for basket_a: {error_a}"

    result_b, error_b = execute_sql(cursor, sql_b)
    if error_b:
        return f"Error executing SQL for basket_b: {error_b}"

    disconnect_from_db(connection, cursor)

    # Prepare the fruits data for rendering in HTML
    fruits_a = [row[0] for row in result_a]  # Extract unique fruits from basket_a
    fruits_b = [row[0] for row in result_b]  # Extract unique fruits from basket_b

    return render_template('unique_fruits.html', fruits_a=fruits_a, fruits_b=fruits_b)



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
