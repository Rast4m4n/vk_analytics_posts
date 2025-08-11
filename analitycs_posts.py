import pandas as pd
import sqlite3

def load_and_prepare_data(filepath):
    """Метод загрузки и подготовки данных, с которыми будем в последующем работать"""
    data_frame = pd.read_csv(filepath)
    data_frame['DateTime'] = pd.to_datetime(data_frame['DateTime'])
    data_frame['hour'] = data_frame['DateTime'].dt.hour
    data_frame['weekday'] = data_frame['DateTime'].dt.weekday
    # Сортируем по дате, чтобы избежать отрицательного значения 
    # и считаем интервал в днях между постами
    data_frame = data_frame.sort_values('DateTime')
    data_frame['days_since_last_post'] = data_frame['DateTime'].diff().dt.total_seconds() / 86400
    return data_frame

def weekday_case_sql():
    return """
        CASE weekday
            WHEN 0 THEN 'Monday'
            WHEN 1 THEN 'Tuesday'
            WHEN 2 THEN 'Wednesday'
            WHEN 3 THEN 'Thursday'
            WHEN 4 THEN 'Friday'
            WHEN 5 THEN 'Saturday'
            WHEN 6 THEN 'Sunday'
        END AS weekday_name
    """


# Запросы SQL 
# По времени выкладывания поста
# По дню недели 
# По интервалам между постами(Самый первый пост не считаем)
def run_queries(conn):
    queries = {
        "По времени выкладывания": """
            SELECT hour, AVG(likes) AS avg_likes, COUNT(*) AS post_count
            FROM vk_posts
            GROUP BY hour
            ORDER BY avg_likes DESC
        """,
        "По дням недели": f"""
            SELECT {weekday_case_sql()}, AVG(likes) AS avg_likes, COUNT(*) AS post_count
            FROM vk_posts
            GROUP BY weekday
            ORDER BY avg_likes DESC
        """,
        "По интервалам между постами": """
            SELECT ROUND(days_since_last_post, 1) AS interval_days, likes
            FROM vk_posts
            WHERE days_since_last_post IS NOT NULL
        """,
        "Общая информация": f"""
            SELECT likes, hour, {weekday_case_sql()}, days_since_last_post
            FROM vk_posts
        """
    }

    for name, query in queries.items():
        print(f'\n--- Результат запроса: {name} ---')
        print(pd.read_sql_query(query, conn))


def calculate_and_describe_correlations(df):
    """Вычисляем по какому параметру большая корреляция с лайками"""
    # Корреляция по методу Пирсона
    corr = df.corr(method='pearson', numeric_only=True)['Likes'].drop('Likes', errors='ignore')

    # Записываем направление и силу связи по коэффициенту
    def strength_and_diretcion_coeff(coeff):
        abs_coeff = abs(coeff)
        if abs_coeff < 0.3:
            strength = "слабая"
        elif abs_coeff < 0.7:
            strength = "умеренная"
        else:
            strength = "сильная"
        direction = "положительная" if coeff > 0 else "отрицательная"
        return strength, direction

    descriptions = []
    # Записываем и выводим каждый параметр и его силу корреляции
    for feature, coeff in corr.items():
        strength, direction = strength_and_diretcion_coeff(coeff)
        descriptions.append(f"Корреляция с '{feature}': {coeff:.3f} — {strength} {direction} связь")
    return "\n".join(descriptions)

def main():
    data_frame = load_and_prepare_data('vk_posts.csv')

    with sqlite3.connect('vk_posts.db') as conn:
        data_frame.to_sql('vk_posts', conn, index=False, if_exists='replace')
        run_queries(conn)

    print("\n---- Корреляция методом Пирсона ----")
    print(calculate_and_describe_correlations(data_frame))


if __name__ == "__main__":
    main()
