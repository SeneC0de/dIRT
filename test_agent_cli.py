"""Tests for agent_cli.py. Run with: python -m unittest test_agent_cli.

These tests monkey-patch the `db` module in agent_cli so no Firestore traffic
happens. They cover the ADR-by-number resolution path that previously caused
ghost docs at /adrs/<number>.
"""
import io
import json
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

import agent_cli


# A representative real Firestore auto-ID — distinct from the ADR number.
REAL_DOC_ID = "eUBul4KLH4bmFn5VtaQg"


def _ns(**kwargs):
    """Lightweight argparse.Namespace stand-in."""
    return types.SimpleNamespace(**kwargs)


class ResolveAdrArgTests(unittest.TestCase):
    def test_digit_string_resolves_to_real_doc_id(self):
        with mock.patch.object(
            agent_cli.db, "get_adr_by_number",
            return_value={"id": REAL_DOC_ID, "number": 68},
        ) as gabn:
            self.assertEqual(agent_cli._resolve_adr_arg("68"), REAL_DOC_ID)
            gabn.assert_called_once_with(68)

    def test_non_digit_string_passes_through(self):
        with mock.patch.object(agent_cli.db, "get_adr_by_number") as gabn:
            self.assertEqual(
                agent_cli._resolve_adr_arg(REAL_DOC_ID),
                REAL_DOC_ID,
            )
            gabn.assert_not_called()

    def test_missing_number_exits_loudly(self):
        with mock.patch.object(agent_cli.db, "get_adr_by_number", return_value=None):
            with self.assertRaises(SystemExit) as cm:
                agent_cli._resolve_adr_arg("999")
            self.assertIn("999", str(cm.exception))


class UpdateAdrByNumberTests(unittest.TestCase):
    def test_update_by_number_patches_real_doc_not_ghost(self):
        """The original bug: `update-adr 68 --body-file ...` patched /adrs/68
        instead of resolving 68 -> doc ID eUBul4...; this test pins the fix."""
        args = _ns(
            adr_id="68",
            number=None, title=None, url=None, status=None,
            author=None, decision_date=None, description=None,
            body=None, body_file=None,
        )
        # Inject a body so there's something to patch.
        args.body = "## Amendment\n\nbody text"

        with mock.patch.object(
            agent_cli.db, "get_adr_by_number",
            return_value={"id": REAL_DOC_ID, "number": 68},
        ) as gabn, mock.patch.object(
            agent_cli.db, "update_adr"
        ) as upd:
            buf = io.StringIO()
            with redirect_stdout(buf):
                agent_cli.cmd_update_adr(args)

        gabn.assert_called_once_with(68)
        # Critical assertion: update_adr called with the REAL doc ID, not "68".
        upd.assert_called_once()
        called_doc_id = upd.call_args.args[0]
        self.assertEqual(called_doc_id, REAL_DOC_ID)
        self.assertNotEqual(called_doc_id, "68")
        # And the JSON output reports the real doc id.
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["adr_id"], REAL_DOC_ID)
        self.assertIn("body", payload["updated"])

    def test_update_by_real_doc_id_passes_through(self):
        args = _ns(
            adr_id=REAL_DOC_ID,
            number=None, title=None, url=None, status="accepted",
            author=None, decision_date=None, description=None,
            body=None, body_file=None,
        )
        with mock.patch.object(agent_cli.db, "get_adr_by_number") as gabn, \
             mock.patch.object(agent_cli.db, "update_adr") as upd:
            buf = io.StringIO()
            with redirect_stdout(buf):
                agent_cli.cmd_update_adr(args)
        gabn.assert_not_called()
        upd.assert_called_once()
        self.assertEqual(upd.call_args.args[0], REAL_DOC_ID)


class DeleteAdrByNumberTests(unittest.TestCase):
    def test_delete_by_number_deletes_real_doc(self):
        args = _ns(adr_id="68")
        with mock.patch.object(
            agent_cli.db, "get_adr_by_number",
            return_value={"id": REAL_DOC_ID, "number": 68},
        ), mock.patch.object(agent_cli.db, "delete_adr") as dele:
            buf = io.StringIO()
            with redirect_stdout(buf):
                agent_cli.cmd_delete_adr(args)
        dele.assert_called_once_with(REAL_DOC_ID)


if __name__ == "__main__":
    unittest.main()
