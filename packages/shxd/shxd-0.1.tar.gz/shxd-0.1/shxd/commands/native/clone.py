
import requests
import base64
import itertools
import re
import sys
from ...utils import Colors

exclude_backlist = [
    "bash", "shell","console", "powershell", "cmd", "terminal", "console", "prompt", "command", "line", "cli", "js", "py", "html", "script"
]
install_steps_keywords = [
    "Instalação", "Installing","Installation","Setup", "Install", "Setup", "Setup", "Running", "Rodando", "Run","Deployment"
]   


def extract_between_markers(txt:str) -> list:
    pattern = r'```(.*?)```|`(.*?)`'
    matches = re.findall(pattern, txt, re.DOTALL)
    results = []
    for match in matches:
        resultado = match[0] if match[0] else match[1]

        results.append(resultado.strip())
        
    return results


def get_suggestions(owner: str, repo: str):
    api_url = f'https://api.github.com/repos/{owner}/{repo}/readme'
    response = requests.get(api_url)

    if response.status_code == 200:
        readme_content = base64.b64decode(response.json()['content']).decode('utf-8')
        after_installation = None
        for keyword in install_steps_keywords:
            if keyword in readme_content:
                after_installation = readme_content.split(keyword)[1]
                resultados = extract_between_markers(after_installation)

                resultados_separados = [bloco.split('\n') for bloco in resultados if len(bloco) > 0]
                url = ''
                results = list(itertools.chain(*resultados_separados))
                filtered_results = []

                for item in results:
                    if item not in exclude_backlist:
                        if item.startswith('$ '):
                            item = item[2:]
                        if item.startswith('git clone'): 
                            # Skip 'cd' command if it's right after 'git clone'
                            if results and results[results.index(item) + 1].startswith('cd'):
                                continue
                            continue
                        if item.startswith('http://') or item.startswith('https://'):
                            url = item
                            continue
                        if item.startswith('/'):
                            continue
                        filtered_results.append(item)

                return filtered_results
    else:
        return None



def clone(url:str):
    owner, repo = url.strip().split('/')[-2:]
    readme_install_sugesstions = get_suggestions(owner, repo)
    if readme_install_sugesstions:
        sys.stdout.write(f"""\n 🌐 {Colors().cyan}{owner}{Colors().reset}, the owner of this repository, recommended that you use the commands below to run the project:\n\n""")
        for i, suggestion in enumerate(readme_install_sugesstions, start=1):
            sys.stdout.write(f'  {Colors().cyan}{i}{Colors().reset}. {suggestion} \n')
    else:
        print('No installation instructions found in README')
    
    sys.stdout.write(f'\n{Colors().red} 🛑 Before executing commands from strangers, ensure that they are safe and cannot damage your machine.{Colors().reset}')
    sys.stdout.write(f'\n{Colors().yellow} ⚠️ Do you really want to run all these commands sequentially?{Colors().reset} (Y/N): ')
    sys.stdout.flush()
    entrada = sys.stdin.readline().strip()  

    if entrada.lower() in ['y', 'yes']:
        sys.stdout.write('Executing commands...\n')
    else:
        sys.stdout.write('Aborting...\n')