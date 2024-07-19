from ..shapes import Shape


def exportVTP(
    shape: Shape, fname: str, tolerance: float = 0.1, angularTolerance: float = 0.1
):
    from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter

    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(fname)
    writer.SetInputData(shape.toVtkPolyData(tolerance, angularTolerance))
    writer.Write()


def toString(
    shape: Shape, tolerance: float = 1e-3, angularTolerance: float = 0.1
) -> str:
    from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter

    writer = vtkXMLPolyDataWriter()
    writer.SetWriteToOutputString(True)
    writer.SetInputData(shape.toVtkPolyData(tolerance, angularTolerance, True))
    writer.Write()

    return writer.GetOutputString()
