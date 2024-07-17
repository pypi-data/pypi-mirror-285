json_data = {
    "items": [
        {
            "id": 607,
            "source": {
                "artifact": {
                    "api": "bitbucket",
                    "branch_name": "develop",
                    "commit_id": "",
                    "content": "  test('User enters valid TL server URL in the WBE', async () => {\n    /*\n        Scenario 8 - User enters valid TL server URL in the WBE\n         */\n    const domain = process.env.TL_DOMAIN;\n    const username = process.env.TL_USERNAME;\n    const password = process.env.TL_PASSWORD;\n    const TLExtensionPath = await extensionPath(browser);\n\n    try {\n      await wbePage.goto(TLExtensionPath);\n      await setTLDomain(wbePage, TLExtensionPath, domain);\n      await setTlUserCredentials(wbePage, TLExtensionPath, username, password);\n      await wbePage.waitForSelector('#project_list_container', { timeout: 5000 });\n    } catch (error) {\n      throw error; // Rethrow the error to fail the test\n    } finally {\n      await clearPageData(wbePage);\n    }\n  }, 15000);\n",
                    "description": "",
                    "id": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-28:47",
                    "link": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-28:47",
                    "title": "browser.spec.js",
                    "title_label": "User enters valid TL server URL in the WBE",
                }
            },
            "target": {
                "artifact": {
                    "api": "testrail",
                    "branch_name": "",
                    "commit_id": "",
                    "content": "",
                    "description": None,
                    "id": "https://tracelynx.testrail.io/index.php?/cases/view/3405",
                    "link": "https://tracelynx.testrail.io/index.php?/cases/view/3405",
                    "title": "browser.spec.js",
                    "title_label": "user_enters_valid_tl_server_url_in_the_wbe",
                }
            },
            "traceability_matrix": {"id": 3, "name": "Traceability Matrix"},
        },
        {
            "id": 608,
            "source": {
                "artifact": {
                    "api": "bitbucket",
                    "branch_name": "develop",
                    "commit_id": "",
                    "content": "  test('User enters invalid TL server URL in the WBE', async () => {\n    /*\n        Scenario 9 - User enters invalid TL server URL in the WBE\n         */\n    const domain = 'http://invalid.tl.server.com';\n    const TLExtensionPath = await extensionPath(browser);\n\n    try {\n      await wbePage.goto(TLExtensionPath);\n      await setTLDomain(wbePage, TLExtensionPath, domain, false);\n      await wbePage.waitForSelector('#infoURL', { timeout: 5000, visible: true });\n\n      // Check if the element is visible\n      const isVisible = await wbePage.evaluate(() => {\n        const element = document.querySelector('#infoURL');\n        if (!element) {\n          return false;\n        }\n        const style = window.getComputedStyle(element);\n        return style && style.display !== 'none';\n      });\n\n      if (isVisible) {\n        console.log('Element is visible');\n      } else {\n        console.log('Element exists but is not visible');\n      }\n\n      const errorMessageAppears = await wbePage.evaluate(() => {\n        const div = document.querySelector('#infoURL');\n        return div.innerHTML.includes('Invalid TraceLynx server URL');\n        // return div.textContent.includes('Invalid TraceLynx server URL');\n      });\n\n      if (!errorMessageAppears) {\n        throw new Error('Error message did not appear');\n      } else {\n        console.log('The message \"Invalid TraceLynx server URL\" appeared');\n      }\n    } catch (error) {\n      throw error; // Rethrow the error to fail the test\n    } finally {\n      await clearPageData(wbePage);\n    }\n  }, 15000);\n",
                    "description": "",
                    "id": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-49:93",
                    "link": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-49:93",
                    "title": "browser.spec.js",
                    "title_label": "User enters invalid TL server URL in the WBE",
                }
            },
            "target": {
                "artifact": {
                    "api": "testrail",
                    "branch_name": "",
                    "commit_id": "",
                    "content": "",
                    "description": None,
                    "id": "https://tracelynx.testrail.io/index.php?/cases/view/4164",
                    "link": "https://tracelynx.testrail.io/index.php?/cases/view/4164",
                    "title": "User enters invalid TL server URL in the WBE",
                    "title_label": "User enters invalid TL server URL in the WBE",
                }
            },
            "traceability_matrix": {"id": 3, "name": "Traceability Matrix"},
        },
        {
            "id": 609,
            "source": {
                "artifact": {
                    "api": "bitbucket",
                    "branch_name": "develop",
                    "commit_id": "",
                    "content": "  test('User logs into TL WBE with valid credentials', async () => {\n    /*\n        Scenario 10 - User logs into TL WBE with valid credentials\n         */\n    const domain = process.env.TL_DOMAIN;\n    const username = process.env.TL_USERNAME;\n    const password = process.env.TL_PASSWORD;\n\n    const TLExtensionPath = await extensionPath(browser);\n\n    try {\n      await wbePage.goto(TLExtensionPath);\n      await setTLDomain(wbePage, TLExtensionPath, domain);\n      await setTlUserCredentials(wbePage, TLExtensionPath, username, password);\n      await wbePage.waitForSelector('#project_list_container', { timeout: 5000 });\n    } catch (error) {\n      throw error; // Rethrow the error to fail the test\n    } finally {\n      await clearPageData(wbePage);\n    }\n  }, 15000);\n",
                    "description": "",
                    "id": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-95:115",
                    "link": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-95:115",
                    "title": "browser.spec.js",
                    "title_label": "User logs into TL WBE with valid credentials",
                }
            },
            "target": {
                "artifact": {
                    "api": "testrail",
                    "branch_name": "",
                    "commit_id": "",
                    "content": "",
                    "description": None,
                    "id": "https://tracelynx.testrail.io/index.php?/cases/view/3405",
                    "link": "https://tracelynx.testrail.io/index.php?/cases/view/3405",
                    "title": "User enters valid TL server URL in the WBE",
                    "title_label": "User enters valid TL server URL in the WBE",
                }
            },
            "traceability_matrix": {"id": 3, "name": "Traceability Matrix"},
        },
        {
            "id": 610,
            "source": {
                "artifact": {
                    "api": "bitbucket",
                    "branch_name": "develop",
                    "commit_id": "",
                    "content": "  test('User logs into TL WBE with invalid credentials', async () => {\n    /*\n        Scenario 11 - User logs into TL WBE with invalid credentials\n         */\n    const domain = process.env.TL_DOMAIN;\n    const username = process.env.TL_USERNAME;\n    const password = 'password';\n    const TLExtensionPath = await extensionPath(browser);\n\n    try {\n      await setTLDomain(wbePage, TLExtensionPath, domain);\n      await setTlUserCredentials(wbePage, TLExtensionPath, username, password);\n      await wbePage.waitForSelector('#infoURL', { timeout: 5000, visible: true });\n\n      const errorMessageAppears = await wbePage.evaluate(() => {\n        const div = document.getElementById('infoURL');\n        return div.textContent.includes('Invalid user credentials');\n      });\n\n      if (!errorMessageAppears) {\n        throw new Error('Invalid credentials message not found');\n      }\n    } catch (error) {\n      throw error; // Rethrow the error to fail the test\n    } finally {\n      await clearPageData(wbePage);\n    }\n  }, 15000);\n",
                    "description": "",
                    "id": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-117:144",
                    "link": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-117:144",
                    "title": "browser.spec.js",
                    "title_label": "User logs into TL WBE with invalid credentials",
                }
            },
            "target": {
                "artifact": {
                    "api": "testrail",
                    "branch_name": "",
                    "commit_id": "",
                    "content": "",
                    "description": None,
                    "id": "https://tracelynx.testrail.io/index.php?/cases/view/4162",
                    "link": "https://tracelynx.testrail.io/index.php?/cases/view/4162",
                    "title": "User logs into TL WBE with invalid credentials",
                    "title_label": "User logs into TL WBE with invalid credentials",
                }
            },
            "traceability_matrix": {"id": 3, "name": "Traceability Matrix"},
        },
        {
            "id": 611,
            "source": {
                "artifact": {
                    "api": "bitbucket",
                    "branch_name": "develop",
                    "commit_id": "",
                    "content": "  test('User can navigate to Jira project from WBE', async () => {\n    /*\n        Scenario 12 - User can navigate to Jira project from WBE\n         */\n    const domain = process.env.TL_DOMAIN;\n    const username = process.env.TL_USERNAME;\n    const password = process.env.TL_PASSWORD;\n    const TLExtensionPath = await extensionPath(browser);\n\n    try {\n      await wbePage.goto(TLExtensionPath);\n      await setTLDomain(wbePage, TLExtensionPath, domain);\n      await setTlUserCredentials(wbePage, TLExtensionPath, username, password);\n      await wbePage.waitForSelector('#project_list_container', {\n        timeout: 5000,\n        visible: true,\n      });\n      await wbePage.waitForSelector('#project_list_container > div', {\n        timeout: 5000,\n        visible: true,\n      });\n\n      // Check the src attribute of the img element to see if it matches the expected URL for the icon\n      const project = await wbePage.evaluate(() => {\n        const projects = Array.from(document.querySelectorAll('#project_list_container > div'));\n        for (const project of projects) {\n          const img = project.querySelector('img');\n          if (img && img.src.includes('jira_logo.png')) {\n            const name = project.querySelector('a').textContent.trim();\n            const link = project.querySelector('a').href;\n            return { name, link };\n          }\n        }\n        return null;\n      });\n      if (!project) {\n        throw new Error('Jira project not found');\n      } else {\n        console.log('Jira project found');\n      }\n      await wbePage.goto(project.link);\n    } catch (error) {\n      throw error; // Rethrow the error to fail the test\n    } finally {\n      await clearPageData(wbePage);\n    }\n  }, 15000);\n",
                    "description": "",
                    "id": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-146:192",
                    "link": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-146:192",
                    "title": "browser.spec.js",
                    "title_label": "User can navigate to Jira project from WBE",
                }
            },
            "target": {
                "artifact": {
                    "api": "testrail",
                    "branch_name": "",
                    "commit_id": "",
                    "content": "",
                    "description": None,
                    "id": "https://tracelynx.testrail.io/index.php?/cases/view/4165",
                    "link": "https://tracelynx.testrail.io/index.php?/cases/view/4165",
                    "title": "User can navigate to Jira project from WBE",
                    "title_label": "User can navigate to Jira project from WBE",
                }
            },
            "traceability_matrix": {"id": 3, "name": "Traceability Matrix"},
        },
        {
            "id": 612,
            "source": {
                "artifact": {
                    "api": "bitbucket",
                    "branch_name": "develop",
                    "commit_id": "",
                    "content": "  test('User can navigate to Gitlab project from WBE', async () => {\n    /*\n        Scenario 13 - User can navigate to Gitlab project from WBE\n         */\n    const domain = process.env.TL_DOMAIN;\n    const username = process.env.TL_USERNAME;\n    const password = process.env.TL_PASSWORD;\n    const TLExtensionPath = await extensionPath(browser);\n\n    try {\n      await wbePage.goto(TLExtensionPath);\n      await clearPageData(wbePage);\n      await setTLDomain(wbePage, TLExtensionPath, domain);\n      await setTlUserCredentials(wbePage, TLExtensionPath, username, password);\n      await wbePage.waitForSelector('#project_list_container', {\n        timeout: 5000,\n        visible: true,\n      });\n      await wbePage.waitForSelector('#project_list_container > div', {\n        timeout: 5000,\n        visible: true,\n      });\n\n      // Check the src attribute of the img element to see if it matches the expected URL for the icon\n      const project = await wbePage.evaluate(() => {\n        const projects = Array.from(document.querySelectorAll('#project_list_container > div'));\n        for (const project of projects) {\n          const img = project.querySelector('img');\n          if (img && img.src.includes('gitlab_logo.png')) {\n            const name = project.querySelector('a').textContent.trim();\n            const link = project.querySelector('a').href;\n            return { name, link };\n          }\n        }\n        return null;\n      });\n      if (!project) {\n        throw new Error('Gitlab project not found');\n      } else {\n        console.log('Gitlab project found');\n      }\n      await wbePage.goto(project.link);\n    } catch (error) {\n      throw error; // Rethrow the error to fail the test\n    } finally {\n      await clearPageData(wbePage);\n    }\n  }, 15000);\n",
                    "description": "",
                    "id": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-194:241",
                    "link": "https://bitbucket.org/koneksys/generic-wbe/src/develop/tests/browser/browser.spec.js#lines-194:241",
                    "title": "browser.spec.js",
                    "title_label": "User can navigate to Gitlab project from WBE",
                }
            },
            "target": {
                "artifact": {
                    "api": "testrail",
                    "branch_name": "",
                    "commit_id": "",
                    "content": "",
                    "description": None,
                    "id": "https://tracelynx.testrail.io/index.php?/cases/view/4161",
                    "link": "https://tracelynx.testrail.io/index.php?/cases/view/4161",
                    "title": "User can navigate to GitLab project from WBE",
                    "title_label": "User can navigate to GitLab project from WBE",
                }
            },
            "traceability_matrix": {"id": 3, "name": "Traceability Matrix"},
        },
    ]
}
