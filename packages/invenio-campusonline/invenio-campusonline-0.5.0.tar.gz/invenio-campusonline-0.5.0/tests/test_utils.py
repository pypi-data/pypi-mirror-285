# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module utils."""

from xml.etree.ElementTree import Element, fromstring, tostring

from invenio_campusonline.records.models import CampusOnlineRESTPOSTXML
from invenio_campusonline.types import Embargo, ThesesFilter
from invenio_campusonline.utils import extract_embargo_range


def compare_xml(body: str, expected: str) -> bool:
    """Compare xml."""
    return tostring(fromstring(body)) == tostring(fromstring(expected))


def test_create_request_body_metadata() -> None:
    """Test the create_request_body_metadata function."""
    post_xml = CampusOnlineRESTPOSTXML("token-abc")
    body = post_xml.create_request_body_metadata("abcd")
    expected = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
          <soapenv:Header/>
          <soapenv:Body>
            <bas:getMetadataByThesisIDRequest>
              <bas:token>token-abc</bas:token>
              <bas:ID>abcd</bas:ID>
              <bas:attr key="ALL"/>
              <bas:classAttrKeySet>
                <bas:name>text</bas:name>
                <bas:attr key="ALL"/>
              </bas:classAttrKeySet>
              <bas:classAttrKeySet>
                <bas:name>author</bas:name>
                <bas:attr key="ALL"/>
              </bas:classAttrKeySet>
              <bas:classAttrKeySet>
                <bas:name>supervisor</bas:name>
                <bas:attr key="ALL"/>
              </bas:classAttrKeySet>
            </bas:getMetadataByThesisIDRequest>
          </soapenv:Body>
        </soapenv:Envelope>
    """

    assert compare_xml(body, expected)


def test_create_request_body_download() -> None:
    """Test the create_request_body_download function."""
    post_xml = CampusOnlineRESTPOSTXML("token-abc")
    body = post_xml.create_request_body_download("abcd")
    expected = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
          <soapenv:Header/>
          <soapenv:Body>
            <bas:getDocumentByThesisIDRequest>
              <bas:token>token-abc</bas:token>
              <bas:ID>abcd</bas:ID>
              <bas:docType>VOLLTEXT</bas:docType>
            </bas:getDocumentByThesisIDRequest>
          </soapenv:Body>
        </soapenv:Envelope>
    """
    assert compare_xml(body, expected)


def test_create_request_body_ids() -> None:
    """Test the create_request_body_ids function."""
    post_xml = CampusOnlineRESTPOSTXML("token-abc")
    theses_filter = ThesesFilter("theses-filter-test")

    body = post_xml.create_request_body_ids(theses_filter)

    expected = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
          <soapenv:Header/>
          <soapenv:Body>
            <bas:getAllThesesMetadataRequest>
              <bas:token>token-abc</bas:token>
              {theses_filter}
            </bas:getAllThesesMetadataRequest>
          </soapenv:Body>
        </soapenv:Envelope>
    """
    assert compare_xml(body, expected)

    theses_filter = ThesesFilter(
        """
            <bas:thesesType>DISS</bas:thesesType>
            <bas:state name="IFG"/>
        """,
    )
    body = post_xml.create_request_body_ids(theses_filter)
    expected = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
          <soapenv:Header/>
          <soapenv:Body>
            <bas:getAllThesesMetadataRequest>
              <bas:token>token-abc</bas:token>
              {theses_filter}
            </bas:getAllThesesMetadataRequest>
          </soapenv:Body>
        </soapenv:Envelope>
    """
    assert compare_xml(body, expected)


def test_create_request_header() -> None:
    """Test the create_request_header function."""
    header = CampusOnlineRESTPOSTXML.create_request_header("allThesesMetadataRequest")
    expected = {
        "Content-Type": "application/xml",
        "SOAPAction": "urn:service#allThesesMetadataRequest",
    }

    assert header == expected


def test_extract_embargo_range(minimal_record: Element) -> None:
    """Test the extract_embargo_range function."""
    embargo = extract_embargo_range(minimal_record)

    assert embargo.end_date == "2025-03-03"
    assert bool(Embargo()) is False

    embargo = extract_embargo_range(Element("root"))

    assert bool(embargo) is False

    if not bool(embargo := extract_embargo_range(Element("root"))):
        assert bool(embargo) is False
