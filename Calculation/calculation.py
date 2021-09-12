#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer


class Calculation(BaseHTTPRequestHandler):
    def do_PUT(self):
        self.data_string = self.rfile.read(int(self.headers["Content-Length"]))
        json_payload = json.loads(self.data_string)
        values = [float(data[3]) for data in json_payload]
        sum_value = sum(values)

        avg_value = round(sum_value / len(values), 2)
        sum_value = round(sum_value, 2)

        print(f"result: val_sum: `{sum_value}`; avg: `{avg_value}`")

        self.send_response(HTTPStatus.ACCEPTED)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = json.dumps(
            {"status_code": 201, "response": {"avg": avg_value, "sum": sum_value}}
        )
        self.wfile.write(bytes(response, "utf-8"))
        return


def serve_http(server_class=HTTPServer, handler_class=Calculation):
    server_address = ("", 4001)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except:
        httpd.socket.close()


if __name__ == "__main__":
    serve_http()
