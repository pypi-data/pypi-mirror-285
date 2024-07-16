import smtplib
from ewokscore.task import Task


class EmailTask(
    Task,
    input_names=("subject", "from_addr", "to_addrs", "text"),  # type: ignore
    optional_input_names=("mail_options", "rcpt_options", "host", "port"),  # type: ignore
):
    """
    Generic task to send a simple email
    Uses 'smtps.esrf.fr' so will only work inside esrf
    """

    def run(self):
        port = self.get_input_value("port", 0)
        assert isinstance(port, int), "port is expected to be an int"
        host = self.get_input_value("host", "smtps.esrf.fr")
        server = smtplib.SMTP(host, port, timeout=5)
        server.sendmail(
            self.inputs.from_addr,
            self.inputs.to_addrs,
            f"Subject: {self.inputs.subject}\n\n{self.inputs.text}",
        )
        server.quit()
