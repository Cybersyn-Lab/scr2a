from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import Users
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub, DataCatalog
from diagrams.gcp.compute import AppEngine, Functions, GPU, ComputeEngine, GKE
from diagrams.gcp.database import BigTable, Spanner, Firestore, SQL, Datastore
from diagrams.gcp.storage import GCS

with Diagram("Референсная архитектура робота сервисного центра"):
    users = Users("Пользователи")
    analytics = Users("Аналитики заказчика")
    modellers = Users("Модельеры исполнителя")

    with Cluster("Корпоративные сиcтемы"):
        itsm = GCS("ITSM")
        exchange = GCS("Exchange")
        teams = GCS("Teams")
        msad = GCS("AD")
        confluence = GCS("Confluence")

    with Cluster("Кластер с компонентами робота"):
        with Cluster("Основной бизнес-процесс"):
            with Cluster("Обработка входящего трафика"):
                emailmod = GKE("Обработка писем")
                msgmod = GKE("Обработка сообщений")
            with Cluster("Общие компоненты"):
                ocr = GKE("OCR")
                s2t = GKE("Speech to Text")
                t2s = GKE("Text to Speech")
                cls = GKE("Text Classifiers")
                ceph = GCS("Object Storage")
            with Cluster("База знаний"):
                kb = GCS("База знаний Вопрос/Ответ")
                kbmod = GKE("Сервис актуализации БЗВО")

            emailmod >> Edge(color="blue", label="запрос [gRPC]") >> ocr
            emailmod >> Edge(color="blue", label="запрос [gRPC]") >> s2t
            emailmod >> Edge(color="blue", label="запрос [gRPC]") >> t2s
            emailmod >> Edge(color="blue", label="запрос [gRPC]") >> cls
            emailmod >> Edge(color="blue", label="запрос [gRPC]") >> kb
            emailmod >> Edge(color="blue", label="запись файла [HTTPS]") >> ceph
            msad << Edge(color="blue", label="авторизация пользователя [HTTPS]") << emailmod

            msgmod >> Edge(color="blue", label="запрос [gRPC]") >> ocr
            msgmod >> Edge(color="blue", label="запрос [gRPC]") >> s2t
            msgmod >> Edge(color="blue", label="запрос [gRPC]") >> t2s
            msgmod >> Edge(color="blue", label="запрос [gRPC]") >> cls
            msgmod >> Edge(color="blue", label="запрос [gRPC]") >> kb
            msgmod >> Edge(color="blue", label="запись файла [HTTPS]") >> ceph
            msad << Edge(color="blue", label="авторизация пользователя [HTTPS]") << msgmod

            t2s >> Edge(color="blue", label="запись файла [HTTPS]") >> ceph
            [ocr, s2t] << Edge(color="blue", label="чтение файла [HTTPS]") << ceph
            [emailmod, msgmod] << Edge(color="blue", label="чтение/запись файла [HTTPS]") >> ceph

            confluence << Edge(color="blue", label="чтение данных [HTTPS]") << kbmod
            itsm << Edge(color="blue", label="чтение данных [HTTPS]") << kbmod
            kb << Edge(color="blue", label="актуализация БДВО [JDBC]") << kbmod

        with Cluster("Data Operations Workflow"):
            fabric = Dataflow("Data Fabric")
            etl = GKE("Online ETL")
            align = GKE("Data Aligner")
            datalake = Datastore("Log Storage")
            catalog = DataCatalog("Data Catalog")

            emailmod >> Edge(color="blue", label="logging [HTTPS]") >> datalake
            msgmod >> Edge(color="blue", label="logging [HTTPS]") >> datalake
            datalake >> Edge(color="blue", label="batching [JDBC]") >> etl
            etl >> Edge(color="blue", label="batching [JDBC]") >> catalog
            catalog >> Edge(color="blue", label="batching [JDBC]") >> align
            align >> Edge(color="blue", label="batching [JDBC]") >> fabric

        with Cluster("ML Operations Workflow"):
            textomator = GKE("Workflow Processor")
            jupyter = GKE("Jupyter Notebook")
            mlops = GKE("Task Processor")

            catalog >> Edge(color="blue", label="batching [JDBC]") >> textomator
            catalog >> Edge(color="blue", label="batching [JDBC]") >> jupyter
            fabric >> Edge(color="blue", label="batching [JDBC]") >> textomator
            fabric >> Edge(color="blue", label="batching [JDBC]") >> jupyter
            mlops << Edge(color="blue", label="запуск задач [gRPC]") << textomator
            mlops << Edge(color="blue", label="запуск задач [gRPC]") << jupyter

    users >> Edge(color="blue", label="заявки [HTTPS]") >> itsm
    users << Edge(color="blue", label="письма и ответы [IMAP/SMTP]") >> exchange
    users << Edge(color="blue", label="сообщения и вопросы [HTTPS]") >> teams
    itsm >> Edge(color="blue", label="заявки [HTTPS]") >> emailmod
    exchange << Edge(color="blue", label="письма и уведомления [IMAP/SMTP]") >> itsm
    teams >> Edge(color="blue", label="сообщения [HTTPS]") >> msgmod
    emailmod >> Edge(color="blue", label="переадресация [gRPC]") >> msgmod

    itsm << Edge(color="blue", label="заявки [HTTPS]") << emailmod
    itsm << Edge(color="blue", label="заявки [HTTPS]") << msgmod
    textomator << Edge(color="blue", label="верификация словарей и меток [HTTPS]") << analytics
    jupyter << Edge(color="blue", label="обучение и тестирование [HTTPS]") << modellers
