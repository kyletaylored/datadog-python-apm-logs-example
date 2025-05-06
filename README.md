# Celery Logger with Datadog Tracing and Log Injection

This project is a minimal Celery app that:

- Runs periodic logging tasks
- Supports Datadog APM trace correlation
- Supports flexible logging output:
  - JSON or plain text logs
  - File, STDOUT, or syslog destinations
  - Correlated or non-correlated format

## Dependencies

```bash
pip install celery redis ddtrace python-json-logger
```

Redis must also be running locally or in a container:

```bash
docker run -d -p 6379:6379 redis
```

---

Certainly — here’s the updated `README.md` section that includes your exact `conf.yaml` configuration for the Datadog Agent:

---

## Datadog Agent Configuration

To ingest logs using the Datadog Agent:

### Enable logs in `datadog.yaml`:

```yaml
logs_enabled: true
```

### Example log source for file (`conf.d/python.d/conf.yaml`):

```yaml
logs:
  - type: file
    path: "/tmp/celery_tasks.log"
    service: celery-app
    source: python
    sourcecategory: sourcecode
```

> Place this file at: `/etc/datadog-agent/conf.d/python.d/conf.yaml`

### Example log source for syslog (`conf.d/syslog.d/conf.yaml`):

```yaml
logs:
  - type: udp
    port: 514
    source: syslog
    service: celery-app
```

Then restart the Datadog Agent to apply the changes:

```bash
sudo service datadog-agent restart
```

---

## Usage

Run the app using the `start.sh` launcher script.

```bash
chmod +x start.sh
./start.sh
```

### Environment Variables

| Variable             | Description                                           | Default                 |
| -------------------- | ----------------------------------------------------- | ----------------------- |
| `DD_ENV`             | Datadog environment tag                               | `dev`                   |
| `DD_SERVICE`         | Set automatically (`celery-worker`, `celery-runner`)  | —                       |
| `DD_VERSION`         | Version tag for Datadog                               | `1.0`                   |
| `DD_LOGS_INJECTION`  | Enables trace context injection for log correlation   | `true`                  |
| `DD_TRACE_AGENT_URL` | Datadog trace agent URL (if different than default)   | `http://localhost:8126` |
| `LOG_FORMAT`         | Log output format (`json` or `text`)                  | `json`                  |
| `LOG_OUTPUT`         | Log destination (`stdout`, `file`, or `syslog`)       | `stdout`                |
| `LOG_FILE_PATH`      | Path to log file if using file output                 | `/tmp/celery_tasks.log` |
| `SYSLOG_ADDRESS`     | Syslog target (`/dev/log` or `host:port`)             | `/dev/log`              |
| `LOG_CORRELATED`     | Whether to include Datadog trace fields in log output | `true`                  |

---

## Logging Matrix

Here are example commands to run each combination of log format, output, and correlation style.

### JSON Logs

| Output | Correlated | Example Command                                                                                  |
| ------ | ---------- | ------------------------------------------------------------------------------------------------ |
| stdout | yes        | `LOG_FORMAT=json LOG_OUTPUT=stdout LOG_CORRELATED=true ./start.sh`                               |
| stdout | no         | `LOG_FORMAT=json LOG_OUTPUT=stdout LOG_CORRELATED=false ./start.sh`                              |
| file   | yes        | `LOG_FORMAT=json LOG_OUTPUT=file LOG_CORRELATED=true ./start.sh`                                 |
| file   | no         | `LOG_FORMAT=json LOG_OUTPUT=file LOG_CORRELATED=false ./start.sh`                                |
| syslog | yes        | `LOG_FORMAT=json LOG_OUTPUT=syslog SYSLOG_ADDRESS=localhost:514 LOG_CORRELATED=true ./start.sh`  |
| syslog | no         | `LOG_FORMAT=json LOG_OUTPUT=syslog SYSLOG_ADDRESS=localhost:514 LOG_CORRELATED=false ./start.sh` |

### Text Logs

| Output | Correlated | Example Command                                                                                  |
| ------ | ---------- | ------------------------------------------------------------------------------------------------ |
| stdout | yes        | `LOG_FORMAT=text LOG_OUTPUT=stdout LOG_CORRELATED=true ./start.sh`                               |
| stdout | no         | `LOG_FORMAT=text LOG_OUTPUT=stdout LOG_CORRELATED=false ./start.sh`                              |
| file   | yes        | `LOG_FORMAT=text LOG_OUTPUT=file LOG_CORRELATED=true ./start.sh`                                 |
| file   | no         | `LOG_FORMAT=text LOG_OUTPUT=file LOG_CORRELATED=false ./start.sh`                                |
| syslog | yes        | `LOG_FORMAT=text LOG_OUTPUT=syslog SYSLOG_ADDRESS=localhost:514 LOG_CORRELATED=true ./start.sh`  |
| syslog | no         | `LOG_FORMAT=text LOG_OUTPUT=syslog SYSLOG_ADDRESS=localhost:514 LOG_CORRELATED=false ./start.sh` |

Note: Datadog log correlation only works if `LOG_CORRELATED=true` and logs include trace fields. JSON is preferred for structured parsing.

---

## Datadog Agent Configuration

To ingest logs using the Datadog Agent:

### Enable logs in `datadog.yaml`:

```yaml
logs_enabled: true
```

### Example log source for file:

```yaml
# conf.d/python.d/conf.yaml
logs:
  - type: file
    path: /tmp/celery_tasks.log
    service: celery-app
    source: python
```

### Example log source for syslog:

```yaml
# conf.d/syslog.d/conf.yaml
logs:
  - type: udp
    port: 514
    source: syslog
    service: celery-app
```

Restart the agent after changes:

```bash
sudo service datadog-agent restart
```

---

## Developer Notes

- `tasks.py` reads from environment variables to configure logging behavior
- `runner.py` continuously submits tasks to generate log activity
- `start.sh` assigns separate Datadog service names for worker and runner
- Use `DD_TRACE_AGENT_URL` if you're not using the default agent port or host

---

## Project Structure

```
.
├── tasks.py          # Celery app and logger config
├── runner.py         # Periodic task submitter
├── start.sh          # Entry point with log/trace config
├── README.md         # This file
```

---

## Datadog Verification

- Check logs in Datadog Logs Explorer
- Check traces in APM > Services > celery-worker
- Check that logs and traces are linked in the trace viewer (when correlated)

---

## Cleanup

Stop the Redis container (if used):

```bash
docker rm -f $(docker ps -q --filter ancestor=redis)
```

Kill any background Celery workers:

```bash
pkill -f "celery -A tasks"
```
