from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

s1_db = os.getenv("S1_DB")
s2_db = os.getenv("S2_DB")


def _require_database_url(value, name):
    if not value:
        raise ValueError(f"{name} is not set in environment")
    return value

bats = ['327', '11']
MSK_TZ = timezone(timedelta(hours=3))

# ===== СЕРВЕР 1 =====
engine1 = create_engine(_require_database_url(s1_db, "S1_DB"), echo=False, pool_pre_ping=True)
Base1 = declarative_base()
Session1 = sessionmaker(bind=engine1)

# ===== СЕРВЕР 2 =====
engine2 = create_engine(_require_database_url(s2_db, "S2_DB"), echo=False, pool_pre_ping=True)
Base2 = declarative_base()
Session2 = sessionmaker(bind=engine2)

# Словарь для удобного доступа к БД серверов
servers_config = {
    1: {'engine': engine1, 'Base': Base1, 'Session': Session1},
    2: {'engine': engine2, 'Base': Base2, 'Session': Session2}
}


def create_bat_model(bat_id, base):
    """Создаёт модель для батальона"""
    class_name = f"BatPlayer_{bat_id}"
    BatPlayer = type(
        class_name,
        (base,),
        {
            "__tablename__": f"bat_{bat_id}",
            "__module__": __name__,
            "id": Column(Integer, primary_key=True, autoincrement=True),
            "nickname": Column(String, nullable=False),
            "date": Column(String, nullable=False),
            "ticks": Column(Integer, nullable=False),
            "__repr__": lambda self: (
                f"<BatPlayer(id={self.id}, nickname='{self.nickname}', date='{self.date}', ticks={self.ticks})>"
            ),
        },
    )
    return BatPlayer


def init_db():
    """Инициализирует БД обоих серверов и создаёт таблицы"""
    # Создаём таблицы для сервера 1
    bat_models_s1 = {bat: create_bat_model(bat, Base1) for bat in bats}
    servers_config[1]['engine'].metadata = Base1.metadata
    Base1.metadata.create_all(servers_config[1]['engine'])
    
    # Создаём таблицы для сервера 2
    bat_models_s2 = {bat: create_bat_model(bat, Base2) for bat in bats}
    servers_config[2]['engine'].metadata = Base2.metadata
    Base2.metadata.create_all(servers_config[2]['engine'])
    
    # Сохраняем модели в конфиг
    servers_config[1]['models'] = bat_models_s1
    servers_config[2]['models'] = bat_models_s2
    
    print("БД инициализирована для обоих серверов", flush=True)


# Инициализируем БД при запуске
init_db()

def update_bats_data(bats_dict, server=1):
    """
    Обновляет данные батальонов в БД.
    
    Args:
        bats_dict: словарь вида {'327': ['nick1', 'nick2'], '11': ['nick3']}
        server: номер сервера (1 или 2)
    """
    config = servers_config[server]
    Session = config['Session']
    bat_models = config['models']
    
    session = Session()
    today = datetime.now(MSK_TZ).date().isoformat()
    
    try:
        for bat_id, nicknames in bats_dict.items():
            BatModel = bat_models.get(bat_id)
            
            if not BatModel:
                continue
            
            for nickname in nicknames:
                # Ищем существующего игрока
                player = session.query(BatModel).filter_by(nickname=nickname).first()
                
                if player is None:
                    # Создаём нового игрока
                    new_player = BatModel(nickname=nickname, date=today, ticks=1)
                    session.add(new_player)
                else:
                    # Обновляем существующего
                    if player.date == today:
                        player.ticks += 1
                    else:
                        player.date = today
                        player.ticks = 1
        
        session.commit()
        print(f"✅ Сервер {server}: БД обновлена", flush=True)
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при обновлении БД (сервер {server}): {e}", flush=True)
    finally:
        session.close()


def get_players_data(nicknames, server=1, bat_id=None):
    """
    Получает данные игроков по списку никнеймов.
    
    Args:
        nicknames: список никнеймов ['nick1', 'nick2', ...]
        server: номер сервера (1 или 2)
        bat_id: ID батальона (например '327'). Если указан, поиск только в его таблице.
    
    Returns:
        Словарь вида {'nick1': ('2026-04-19', 5), 'nick2': ('2026-04-18', 1)}
    """
    config = servers_config[server]
    Session = config['Session']
    bat_models = config['models']
    
    session = Session()
    result = {}
    
    try:
        # Режим поиска только в одном батальоне.
        if bat_id is not None:
            BatModel = bat_models.get(str(bat_id))
            if BatModel is None:
                for nickname in nicknames:
                    result[nickname] = (None, None)
                return result

            for nickname in nicknames:
                player = session.query(BatModel).filter_by(nickname=nickname).first()
                if player:
                    result[nickname] = (player.date, player.ticks)
                else:
                    result[nickname] = (None, None)
            return result

        # Режим старого поведения: поиск по всем батальонам.
        for nickname in nicknames:
            found = False
            for _, BatModel in bat_models.items():
                player = session.query(BatModel).filter_by(nickname=nickname).first()
                if player:
                    result[nickname] = (player.date, player.ticks)
                    found = True
                    break

            if not found:
                result[nickname] = (None, None)
    
    finally:
        session.close()
    
    return result