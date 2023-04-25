import sys
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/data.json":
            return os.path.abspath(self.server.data_json_path)
        return super().translate_path(path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python serve.py /path/to/data.json")
        sys.exit(1)

    data_json_path = sys.argv[1]
    if not os.path.isfile(data_json_path):
        print(f"Error: {data_json_path} is not a valid file.")
        sys.exit(1)

    port = 8000
    handler = CustomHTTPRequestHandler
    handler.extensions_map.update({".json": "application/json"})
    httpd = HTTPServer(("", port), handler)
    httpd.data_json_path = data_json_path

    print(f"Serving on port {port} with data.json from {data_json_path}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
