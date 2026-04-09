#!/usr/bin/env python3
import json
import os
import pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEB = ROOT / 'assets' / 'workflow-studio.html'
DEFAULT_WORKFLOW = ROOT / 'templates' / 'workflow.template.yaml'
PORT = int(os.environ.get('WORKFLOW_UI_PORT', '8765'))


def list_installed_skills():
    skills_root = pathlib.Path.home() / '.hermes' / 'skills'
    names = []
    if skills_root.exists():
        for cat in sorted(skills_root.iterdir()):
            if not cat.is_dir():
                continue
            for sk in sorted(cat.iterdir()):
                if sk.is_dir() and (sk / 'SKILL.md').exists():
                    names.append(sk.name)
    return names


def read_workflow(path):
    p = pathlib.Path(path)
    if not p.exists():
        p = DEFAULT_WORKFLOW
    with p.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f), str(p)


def write_workflow(path, data):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(WEB.read_bytes())
            return
        if u.path == '/api/skills':
            return self._json(200, {'skills': list_installed_skills()})
        if u.path == '/api/workflow':
            wf_path = self.headers.get('X-Workflow-Path', str(DEFAULT_WORKFLOW))
            data, actual = read_workflow(wf_path)
            return self._json(200, {'path': actual, 'workflow': data})
        return self._json(404, {'error': 'not found'})

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(n) if n > 0 else b'{}'
        try:
            body = json.loads(raw.decode('utf-8'))
        except Exception:
            body = {}
        if u.path == '/api/workflow':
            wf = body.get('workflow')
            path = body.get('path', str(DEFAULT_WORKFLOW))
            if not isinstance(wf, dict):
                return self._json(400, {'error': 'workflow must be object'})
            write_workflow(path, wf)
            return self._json(200, {'ok': True, 'path': path})
        return self._json(404, {'error': 'not found'})


def main():
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'Workflow UI running: http://127.0.0.1:{PORT}')
    print(f'Default workflow: {DEFAULT_WORKFLOW}')
    server.serve_forever()


if __name__ == '__main__':
    main()
