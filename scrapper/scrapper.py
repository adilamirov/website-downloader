import logging
import os
from pathlib import Path
from urllib.parse import urlparse, urljoin, urldefrag

import requests
from lxml import html
from lxml.html import tostring


logger = logging.getLogger()


class Document:

    def __init__(self, url: str, base_dir: Path):
        self.url = url
        self.base_dir = base_dir
        self._base_url = urlparse(urljoin(self.url, '/'))
        self._request = None
        self._content_type = None
        self._content = None
        self._parsed_tree = None
        self._document_dir = None
        self._document_path = None

    def download_document(self) -> bytes:
        resp = requests.get(self.url)
        self._content = resp.content
        self._content_type = resp.headers['Content-Type']
        return self._content

    def is_html(self):
        return 'text/html' in self._content_type

    def get_links(self):
        if not self.is_html():
            return ValueError('Cannot extract links from non-HTML documents')
        if not self._parsed_tree:
            self._parsed_tree = html.fromstring(self._content, base_url=self._base_url.geturl())
            self._parsed_tree.make_links_absolute(self._base_url.geturl())
        for el, attrib, link, pos in self._parsed_tree.iterlinks():
            parsed_url = urlparse(link)
            if parsed_url.netloc != self._base_url.netloc or parsed_url.scheme not in ('http', 'https'):
                continue
            yield el, attrib, link, pos

    def get_document_dir(self) -> Path:
        if not self._document_dir:
            self._document_dir = self.get_document_path().parent
        return self._document_dir

    def get_document_path(self) -> Path:
        """
        Produce document local path from URL
        :return: local Path for document
        """
        if not self._document_path:
            parsed_url = urlparse(self.url)
            path_to_file = parsed_url.path.split('/')
            if not path_to_file[-1].endswith('.html') and self.is_html():
                path_to_file.append('index.html')
            self._document_path = self.base_dir.joinpath(parsed_url.netloc, *path_to_file)
        return self._document_path

    def save(self):
        """
        Save document at local path
        :return:
        """
        try:
            self.get_document_dir().mkdir(parents=True, exist_ok=True)
            with self.get_document_path().open('wb') as document_file:
                document_file.write(self._content)
        except Exception as e:
            logger.log(logging.ERROR, e)


class Scrapper:

    def __init__(self, url: str, base_dir: Path, depth: int = 3):
        self.url = url
        self.depth = depth
        self._visited_urls = set()
        self._original_domain = urlparse(url).netloc
        self.base_dir = base_dir

    def run(self):
        self._scrap(self.url, self.depth)
        self._rewrite_links_to_local()

    def _scrap(self, url: str, depth: int):
        if url in self._visited_urls or depth <= 0:
            return
        self._visited_urls.add(url)

        document = Document(url, self.base_dir)
        document.download_document()

        base_domain = '.'.join(urlparse(url).netloc.split('.')[1:])
        self._scrap_links(document, base_domain, depth - 1)

        document.save()

    def _scrap_links(self, document: Document, domain: str, depth: int):
        """
        Go to links in the given document and download them (recursively respecting depth).
        Processes only links in given domain.
        """
        if not document.is_html() or depth <= 0:
            return
        for _, _, link, _ in document.get_links():
            parsed_url = urlparse(link)
            link_domain = parsed_url.netloc
            link_base_domain = '.'.join(link_domain.split('.')[1:])
            if link_base_domain != domain or parsed_url.scheme not in ('http', 'https'):
                continue
            self._scrap(link, depth)

    def _rewrite_links_to_local(self):
        base_url = urlparse(self.url).geturl()
        for dirpath, dirnames, filenames in os.walk(str(self.base_dir)):
            for filename in filenames:
                if not filename.endswith('.html'):
                    continue
                full_path = os.path.join(dirpath, filename)
                parsed_tree = html.parse(full_path).getroot()
                parsed_tree.make_links_absolute(base_url)
                parsed_tree.rewrite_links(self._link_localizer(dirpath))
                with open(full_path, 'wb') as file:
                    file.write(tostring(parsed_tree))

    def _link_localizer(self, dirpath):
        """
        Returns function which parses link and tries to find a local
        document for this link
        :param dirpath: path where to find a document
        :return: function
        """

        def _wrapper(link):
            parsed_link = urlparse(urldefrag(link)[0])
            path_to_file = parsed_link.path.split('/')
            abs_local_path = str(self.base_dir.joinpath(parsed_link.netloc, *path_to_file))
            rel_local_path = os.path.relpath(abs_local_path, dirpath)
            if os.path.isfile(abs_local_path):
                return rel_local_path
            index_html_file = os.path.join(abs_local_path, 'index.html')
            if os.path.isfile(index_html_file):
                return os.path.join(rel_local_path, 'index.html')
            return link

        return _wrapper
