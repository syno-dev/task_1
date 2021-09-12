#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit

import requests

# TODO: replace print's with logger

DB_ADDRESS = os.getenv("DB", "/DB/simple_db.db")
CALCULATION_HOST = str(os.getenv("CAL_HOST", "localhost"))


class ConnectorDB:
    def __init__(self, db_address):
        # for the sake of simplicity, I assumed that the database already exists and has an appropriate schema
        # i created table with statement in sqlite CLI:
        # CREATE TABLE clientsData (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name VARCHAR(64), t TIMESTAMP, v REAL);
        try:
            self.connection = sqlite3.connect(db_address)
        except sqlite3.Error as err:
            print(err)

    def query_executor(self, query, params, commit=False):
        print(f"execute query: `{query};{params}`")
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        if commit:
            self.connection.commit()
        return cursor


class API(BaseHTTPRequestHandler):
    def do_GET(self):
        if str(self.path) == "/health":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"status_code": 200, "message": "ok"})
            self.wfile.write(bytes(response, "utf-8"))
            return
        if str(self.path).split("/")[1] == "calculate":
            time_range_params = parse_qs(urlsplit(self.path).query)
            print(f"params: `{time_range_params}`")
            name = str(self.path).split("/")[2].split("?")[0]
            print(f"req name: `{name}`")
            if not name:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = json.dumps({"status_code": 400, "message": "bad request"})
                self.wfile.write(bytes(response, "utf-8"))
                return
            if time_range_params:
                if "from" not in time_range_params or "to" not in time_range_params:
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = json.dumps(
                        {"status_code": 400, "message": "bad params names"}
                    )
                    self.wfile.write(bytes(response, "utf-8"))
                    return

                print("executing with params")
                query = "select * from `clientsData` where `name` = ? and `t` between ? and ?;"
                result = db.query_executor(
                    query,
                    (name, time_range_params["from"][0], time_range_params["to"][0]),
                )
                rows = result.fetchall()
                print(rows)
            else:
                print("executing without params")
                query = "select * from `clientsData` where `name` = ?;"
                result = db.query_executor(query, (name,))
                rows = result.fetchall()
                print(rows)

            if rows:
                headers = {"Content-type": "application/json", "Accept": "text/plain"}
                url = f"http://{CALCULATION_HOST}:4001"
                request_response = requests.put(
                    url, data=json.dumps(rows), headers=headers
                )
                computed_values = json.loads(request_response.text)
                avg_value = computed_values["response"]["avg"]
                sum_value = computed_values["response"]["sum"]
                response = json.dumps({"avg": avg_value, "sum": sum_value})
            else:
                response = json.dumps({"avg": None, "sum": None})

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))
            return
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"status_code": 404, "message": "not found"})
            self.wfile.write(bytes(response, "utf-8"))
            return

    def do_POST(self):
        if str(self.path) == "/input":
            print(self.path)
            self.data_string = self.rfile.read(int(self.headers["Content-Length"]))
            print(f"raw: {self.data_string}")
            payload = json.loads(self.data_string)
            print(f"json: {payload}")
            query = "insert into clientsData(name, t, v) values (?,?,?)"
            # FIXME: this can be done better ;)
            for data in payload:
                db.query_executor(
                    query, (data["name"], data["t"], data["v"]), commit=True
                )

            self.send_response(HTTPStatus.ACCEPTED)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"status_code": 201, "message": "accepted"})
            self.wfile.write(bytes(response, "utf-8"))
            return

        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"status_code": 404, "message": "not found"})
            self.wfile.write(bytes(response, "utf-8"))


def serve_http(server_class=HTTPServer, handler_class=API):
    server_address = ("", 4000)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except:
        httpd.socket.close()


if __name__ == "__main__":
    db = ConnectorDB(DB_ADDRESS)
    serve_http()
