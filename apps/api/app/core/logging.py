import logging, json
class JsonFormatter(logging.Formatter):
    def format(self, record): return json.dumps({"level":record.levelname,"message":record.getMessage(),"logger":record.name})
def configure_logging():
    handler=logging.StreamHandler(); handler.setFormatter(JsonFormatter()); logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
