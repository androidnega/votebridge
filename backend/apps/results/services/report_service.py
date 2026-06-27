"""Report preparation services for PDF, CSV, and Excel exports."""

import csv
import io
from typing import Any


class ReportService:
    """Prepares structured report payloads from certified election results."""

    def prepare(self, result, report_format: str) -> dict[str, Any]:
        format_key = report_format.lower().strip()
        if format_key == "csv":
            return self.prepare_csv(result)
        if format_key == "pdf":
            return self.prepare_pdf(result)
        if format_key in {"excel", "xlsx"}:
            return self.prepare_excel(result)
        raise ValueError(f"Unsupported report format: {report_format}")

    def prepare_csv(self, result) -> dict[str, Any]:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "election_title",
                "position",
                "candidate",
                "department",
                "vote_count",
                "vote_percentage",
                "is_winner",
            ]
        )
        election_title = result.election.title
        for position in result.standings.get("positions", []):
            for candidate in position.get("candidates", []):
                writer.writerow(
                    [
                        election_title,
                        position.get("position_title"),
                        candidate.get("full_name"),
                        candidate.get("department"),
                        candidate.get("vote_count"),
                        candidate.get("vote_percentage"),
                        candidate.get("is_winner"),
                    ]
                )
        summary = result.standings.get("summary", {})
        writer.writerow([])
        writer.writerow(["turnout_percentage", summary.get("turnout_percentage")])
        writer.writerow(["total_votes_cast", summary.get("total_votes_cast")])
        writer.writerow(["eligible_voters", summary.get("eligible_voters")])
        writer.writerow(["result_status", result.status])
        writer.writerow(["result_hash", result.result_hash])
        if result.certified_at:
            writer.writerow(["certified_at", result.certified_at.isoformat()])
        if result.published_at:
            writer.writerow(["published_at", result.published_at.isoformat()])

        return {
            "format": "csv",
            "filename": f"{election_title.replace(' ', '_')}_results.csv",
            "content_type": "text/csv",
            "content": buffer.getvalue(),
        }

    def prepare_pdf(self, result) -> dict[str, Any]:
        summary = result.standings.get("summary", {})
        sections = []
        for position in result.standings.get("positions", []):
            sections.append(
                {
                    "title": position.get("position_title"),
                    "winners": [
                        c["full_name"]
                        for c in position.get("candidates", [])
                        if c.get("is_winner")
                    ],
                    "rows": position.get("candidates", []),
                }
            )
        return {
            "format": "pdf",
            "filename": f"{result.election.title.replace(' ', '_')}_results.pdf",
            "content_type": "application/pdf",
            "template": "results_report",
            "payload": {
                "election_title": result.election.title,
                "turnout_percentage": float(result.turnout_percentage),
                "total_votes_cast": result.total_votes_cast,
                "eligible_voters": result.eligible_voters,
                "sections": sections,
                "integrity_report": result.integrity_report,
                "certification": {
                    "certified_at": result.certified_at.isoformat() if result.certified_at else None,
                    "certified_by": result.certified_by.get_full_name() if result.certified_by else None,
                    "published_at": result.published_at.isoformat() if result.published_at else None,
                    "result_hash": result.result_hash,
                },
            },
            "note": "PDF rendering delegated to future template engine.",
        }

    def prepare_excel(self, result) -> dict[str, Any]:
        csv_data = self.prepare_csv(result)
        return {
            "format": "excel",
            "filename": csv_data["filename"].replace(".csv", ".xlsx"),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "sheets": [
                {
                    "name": "Results",
                    "rows": csv_data["content"].splitlines(),
                },
                {
                    "name": "Audit Summary",
                    "rows": [
                        ["integrity_valid", result.integrity_report.get("is_valid")],
                        ["blocking_issues", result.integrity_report.get("blocking_issues")],
                    ],
                },
            ],
            "note": "Excel binary generation delegated to future export library.",
        }


report_service = ReportService()
