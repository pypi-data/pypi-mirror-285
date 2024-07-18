from abc import ABC
from pathlib import PurePath, Path
import aiofiles
from ...exceptions import FileError, FileNotFound
from ...template import getTemplateHandler, TemplateHandler
from ...conf import FILE_STORAGES, TASK_PATH


class TemplateSupport(ABC):
    """TemplateSupport.

    Adding Support for Jinja2 Template parser on Components.
    """

    use_template: bool = False

    def __init__(self, **kwargs):
        self._filestore = None
        # Use Template:
        self.use_template: bool = kwargs.pop('use_template', self.use_template)
        self.from_template_dir: bool = kwargs.pop('from_template_dir', False)
        # Template directory
        try:
            template_dir = kwargs["template_dir"]
            del kwargs["template_dir"]
        except KeyError:
            template_dir = None
        # Template Parser:
        self._templateparser: TemplateHandler = None
        if self.use_template is True:
            self._templateparser = getTemplateHandler(newdir=template_dir)

    async def open_templatefile(
        self,
        file: PurePath,
        program: str = None,
        from_template_dir: bool = False,
        **kwargs
    ) -> str:
        if self._filestore is None:
            # we need to calculate which is the filestore
            self._filestore = FILE_STORAGES.get('default')
        if isinstance(file, str):
            file = Path(file)
        if not file.is_absolute():
            # File is relative to TaskStorage:
            if program is None:
                if from_template_dir is True:
                    directory = Path(TASK_PATH).joinpath("templates")
                else:
                    # Get Templates Dir from FileStore
                    directory = self._filestore.get_directory('templates')
                    file = directory.joinpath(file).resolve()
            else:
                if from_template_dir is True:
                    directory = Path(TASK_PATH).parent.joinpath("templates")
                else:
                    directory = Path(TASK_PATH).joinpath(program, "queries")
                file = directory.joinpath(file).resolve()
        if file.exists() and file.is_file():
            content = None
            # open File:
            try:
                async with aiofiles.open(file, "r+") as afp:
                    content = await afp.read()
            except Exception as exc:
                raise FileError(
                    f"{__name__}: Error Opening File: {file}"
                ) from exc
            # check if we need to replace masks
            if hasattr(self, "masks"):
                content = self.mask_replacement(content)
            if self.use_template is True:
                content = self._templateparser.from_string(
                    content,
                    kwargs
                )
            return content
        else:
            raise FileNotFound(
                f"{__name__}: Missing File: {file}"
            )
