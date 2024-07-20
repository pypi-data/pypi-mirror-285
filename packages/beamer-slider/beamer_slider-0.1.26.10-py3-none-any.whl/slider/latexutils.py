from jinjafy import execute_command
import os
import shutil
import subprocess
import glob
import asyncio

def latexmk(texfile,pdf_out=None,shell=True,cleanup=False, Linux=False, compress_pdf=False):
    cdir = os.getcwd()
    texfile = os.path.abspath(texfile)
    dname = os.path.dirname(texfile)
    os.chdir(dname)
    texfile = os.path.basename(texfile)
    CMD = "latexmk -f -g -pdf -shell-escape -interaction=nonstopmode " + texfile
    print("[slider] Running LaTeX command> " + CMD)
    try:
        s = subprocess.check_output(CMD, shell=True)
    except Exception as e:
        print("[slider] " + "-"*50)
        print("[slider] Latexmk encountered problem in:", CMD)
        print("[slider] Log file is")
        with open( f"{texfile[:-4]}.log", 'r') as f:
            log = f.read()
            print(log)
        print("[slider] " + "-"*50)
        print("[slider] END OF LOG")
        raise e

    if pdf_out:
        shutil.copyfile(texfile[:-4]+".pdf", pdf_out)
    else:
        pdf_out = os.path.join(os.path.dirname(texfile), texfile[:-4]+".pdf")

    if cleanup and os.path.exists(pdf_out):
        bft = ['bbl', 'blg', 'fdb_latexmk', 'fls', 'aux', 'synctex.gz', 'log']
        for ex in bft:
            fl = glob.glob(dname + "/*."+ex)
            for f in fl:
                os.remove(f)
    if compress_pdf:
        cmd = f"""gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -e -o _{pdf_out} {pdf_out}"""
        # cmds = [ f"""gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -e -o""", f"{dname}/{pdf_out}", f"{dname}/{pdf_out}"]
        print("Compressing PDF file using command", cmd)
        subprocess.run(cmd, shell=True)
        shutil.move(f"_{pdf_out}", pdf_out)
        print("[done]")
    os.chdir(cdir)
    return pdf_out

async def latexmk_async(texfile, pdf_out=None, cleanup=False):
    cdir = os.getcwd()
    texfile = os.path.abspath(texfile)
    tmp_texfile = texfile
    compiled_pdf = tmp_texfile[:-4] + ".pdf"
    if os.path.isfile(compiled_pdf):
        os.remove(compiled_pdf)

    dname = os.path.dirname(tmp_texfile)
    os.chdir(dname)
    texfile_name = os.path.basename(tmp_texfile)
    CMD = "latexmk -f -g -pdf -shell-escape -interaction=nonstopmode " + os.path.basename(tmp_texfile)
    print("Running LaTeX command>> " + CMD)
    # s = subprocess.check_output(CMD, shell=True)

    process = await asyncio.create_subprocess_shell(CMD, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout = await process.stdout.read()
    stderr = await process.stderr.read()
    state =  await process.wait()
    if state != 0:
        print(stdout)
        print(stderr)
        raise Exception(f"Subprocess failed {state}")

    assert os.path.isfile(compiled_pdf)

    if pdf_out:
        shutil.copyfile(compiled_pdf, pdf_out)
    else:
        # print("compiled pdf", compiled_pdf)
        pdf_out = os.path.join( os.path.dirname(texfile), os.path.basename(compiled_pdf))
        # print("pdf out", pdf_out)

        # shutil.copyfile(compiled_pdf, pdf_out)

        # shutil.copyfile( os.path.join(os.path.dirname(tmp_texfile), tmp_texfile[:-4] + ".pdf"),
        # pdf_out = os.path.join(os.path.dirname(tmp_texfile), tmp_texfile[:-4] + ".pdf")

    if cleanup and os.path.exists(pdf_out):
        bft = ['bbl', 'blg', 'fdb_latexmk', 'fls', 'aux', 'synctex.gz', 'log']
        for ex in bft:
            fl = glob.glob(dname + "/*." + ex)
            for f in fl:
                os.remove(f)

    os.chdir(cdir)

    assert os.path.isfile(pdf_out)
    print("RETURNING PDF FILE", pdf_out)
    return pdf_out

