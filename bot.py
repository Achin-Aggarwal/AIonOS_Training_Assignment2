# from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
# from botbuilder.schema import ChannelAccount, ActivityTypes
# from intent_parser import parse_intent
# from llm import get_llm_response, get_cs_it_response
# from db_connector import (
#     fetch_all_software, 
#     fetch_software_by_names, 
#     get_software_info,
#     search_software_fuzzy
# )
# from card_builder import (
#     build_software_card, 
#     build_software_selection_card,
 
# )
# import os
# import asyncio
# import sys
# import json
# import httpx
# from groq import Groq
# from dotenv import load_dotenv
# from typing import Optional, Dict, Any, List

# load_dotenv()
# SN_INSTANCE = os.getenv("SN_INSTANCE", "").rstrip("/")
# SN_USER = os.getenv("SN_USER")
# SN_PASS = os.getenv("SN_PASS")


# class MyBot(ActivityHandler):
#     async def on_message_activity(self, turn_context: TurnContext):
#         # Handle card submissions
#         if turn_context.activity.value:
#             await self._handle_card_submission(turn_context)
#             return
            
#         user_msg = turn_context.activity.text or ""
#         parsed = parse_intent(user_msg)

#         if parsed["intent"] == "install":
#             await self._handle_install_intent(turn_context, parsed, user_msg)
#         elif parsed["intent"] == "cs_it":
#             await self._handle_cs_it_intent(turn_context, user_msg)
#         else:
#             await self._handle_general_intent(turn_context, user_msg)

#     async def _handle_install_intent(self, turn_context: TurnContext, parsed: dict, user_msg: str):
#         """Handle software installation requests"""
#         apps = parsed["apps"]

#         if not apps:  
#             catalog = fetch_all_software()
#             if not catalog:
#                 await turn_context.send_activity("⚠️ Sorry, no software available in the catalog.")
#                 return
            
#             await turn_context.send_activity("I can help you install software! Here's what's available:")
#             selection_card = build_software_selection_card(catalog)
#             await turn_context.send_activity(MessageFactory.attachment(selection_card))
            
#         elif len(apps) == 1:
#             catalog = fetch_software_by_names(apps)
#             if not catalog:
#                 catalog = search_software_fuzzy(apps[0])
#             if not catalog:
#                 await turn_context.send_activity(
#                     f"⚠️ Sorry, I couldn't find '{apps[0]}' in our software catalog. "
#                     "Try asking 'install software' to see what's available."
#                 )
#                 return

#             for app, versions in catalog.items():
#                 await turn_context.send_activity(f"Great! I found {app.title()} for you:")
#                 card = build_software_card(app, versions)
#                 await turn_context.send_activity(MessageFactory.attachment(card))
                
#         else:
#             catalog = fetch_software_by_names(apps)
#             if not catalog:
#                 await turn_context.send_activity(
#                     "⚠️ Sorry, I couldn't find any of the requested software in the catalog."
#                 )
#                 return

#             found_apps = list(catalog.keys())
#             missing_apps = [app for app in apps if app not in found_apps]
            
#             if missing_apps:
#                 await turn_context.send_activity(
#                     f"⚠️ I couldn't find: {', '.join(missing_apps)}. "
#                     f"But I found these software options for you:"
#                 )
#             else:
#                 await turn_context.send_activity("Great! I found all the software you requested:")

#             for app, versions in catalog.items():
#                 card = build_software_card(app, versions)
#                 await turn_context.send_activity(MessageFactory.attachment(card))

#     async def _handle_cs_it_intent(self, turn_context: TurnContext, user_msg: str):
#         """Handle CS/IT related queries"""
#         await turn_context.send_activity("🤖 Let me help you with that technical question...")
#         reply = get_cs_it_response(user_msg)
#         await turn_context.send_activity(reply)

#     async def _handle_general_intent(self, turn_context: TurnContext, user_msg: str):
#         """Handle general conversation"""
#         reply = get_llm_response(user_msg)
#         await turn_context.send_activity(reply)

#     # ----------------- FIXED METHODS -----------------
#     @staticmethod
#     async def extract_incident_data(user_input: str) -> Dict[str, Any]:
#         """Extract structured JSON incident data from user input safely."""
#         def create_messages(system_msg: str, user_msg: str) -> List[Dict[str, str]]:
#             return [
#                 {"role": "system", "content": system_msg},
#                 {"role": "user", "content": user_msg}
#             ]
        
#         incident_extraction_system_msg = """You are a ServiceNow incident creation assistant. 
#         Return ONLY a JSON object with the following fields:
#         {
#         "short_description": "...",
#         "description": "...",
#         "category": "...",
#         "caller": "Guest"
#         }"""
        
#         client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#         model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
#         prompt = f"Analyze this user input and extract incident information in JSON format: \"{user_input}\""
#         messages = create_messages(incident_extraction_system_msg, prompt)
        
#         completion = client.chat.completions.create(
#             model=model,
#             messages=messages,
#             temperature=0.1,
#             max_tokens=500
#         )
        
#         response_content = completion.choices[0].message.content.strip()
#         print(f"DEBUG - Raw LLM response: {response_content}")  # 👈 log raw response
        
#         # Try parsing JSON safely
#         try:
#             return json.loads(response_content)
#         except json.JSONDecodeError:
#             print("⚠️ LLM response was not valid JSON, falling back to default incident data.")
#             return {
#                 "short_description": user_input,
#                 "description": user_input,
#                 "category": "Software",
#                 "caller": "Guest"
#             }

#     @staticmethod
#     async def create_incident_direct(incident_data: Dict[str, Any]) -> Optional[Dict]:
#         """Create an incident directly in ServiceNow via REST API."""
#         try:
#             print("🔄 Creating incident via ServiceNow API...")
#             url = f"{SN_INSTANCE}/api/now/table/incident"
#             headers = {"Content-Type": "application/json", "Accept": "application/json"}

#             if not incident_data.get("caller"):
#                 incident_data["caller"] = "Guest"

#             async with httpx.AsyncClient() as client:
#                 response = await client.post(url, headers=headers, json=incident_data, auth=(SN_USER, SN_PASS))
#             response.raise_for_status()
#             print("✅ Incident created successfully!")
#             return response.json()
#         except Exception as e:
#             print(f"❌ Error creating incident: {e}")
#             return None
#     # -------------------------------------------------

#     async def _handle_card_submission(self, turn_context: TurnContext):
#         """Handle adaptive card submissions"""
#         try:
#             card_data = turn_context.activity.value
#             action = card_data.get("action", "")
            
#             if action == "install":
#                 app = card_data.get("app", "")
#                 version = card_data.get("version", "")
                
#                 if app and version:
#                     await turn_context.send_activity(
#                         f"🚀 Creating ServiceNow Ticket for Installation of {app.title()} version {version}..."
#                     )
                    
#                     software_info = get_software_info(app, version)
#                     incident_description = f"Installation of {software_info['name']} v{software_info['version']}"

#                     if incident_description:
#                         incident_data = await self.extract_incident_data(incident_description)
#                         result = await self.create_incident_direct(incident_data)
#                         if result:
#                             print(f"DEBUG - Full ServiceNow response: {result}")  # 👈 log full response

#                             # Try to extract incident number safely
#                             incident_number = (
#                                 result.get("result", {}).get("number")
#                                 or result.get("number")
#                                 or "Unknown"
#                             )

#                             print(f"✅ Incident created successfully! Incident Number: {incident_number}")
#                             await turn_context.send_activity(
#                                 f"✅ Incident created successfully! Incident Number: {incident_number}"
#                             )
#                         else:
#                             print("❌ Failed to create incident.")
#                             await turn_context.send_activity("❌ Failed to create incident.")
#                             # CREATING INCIDENT END


                            

                        
                        

                        
#                 else:
#                     await turn_context.send_activity("⚠️ Please select a version to install.")
                    
#             elif action == "show_versions":
#                 selected_software = card_data.get("selected_software", [])
#                 print(f"DEBUG - Received card_data: {card_data}")
#                 print(f"DEBUG - Selected software: {selected_software}")
#                 print(f"DEBUG - Type: {type(selected_software)}")
                
#                 if not selected_software:
#                     await turn_context.send_activity("⚠️ Please select at least one software to install.")
#                     return
                
#                 software_list = []
#                 if isinstance(selected_software, str):
#                     if "," in selected_software:
#                         software_list = [s.strip() for s in selected_software.split(",")]
#                     else:
#                         software_list = [selected_software]
#                 elif isinstance(selected_software, list):
#                     software_list = selected_software
#                 else:
#                     software_list = [str(selected_software)]
                
#                 print(f"DEBUG - Processed software_list: {software_list}")
                
#                 if not software_list:
#                     await turn_context.send_activity("⚠️ Please select at least one software to install.")
#                     return
                
#                 catalog = fetch_software_by_names(software_list)
#                 print(f"DEBUG - Catalog found: {catalog}")
                
#                 if catalog:
#                     found_count = len(catalog)
#                     selected_count = len(software_list)
                    
#                     await turn_context.send_activity(
#                         f"Perfect! Found {found_count} out of {selected_count} selected software. "
#                         f"Here are the installation options:"
#                     )
                    
#                     for app, versions in catalog.items():
#                         card = build_software_card(app, versions)
#                         await turn_context.send_activity(MessageFactory.attachment(card))
                        
#                     found_names = [name.lower() for name in catalog.keys()]
#                     missing = [name for name in software_list if name.lower() not in found_names]
#                     if missing:
#                         await turn_context.send_activity(f"⚠️ Couldn't find: {', '.join(missing)}")
#                 else:
#                     await turn_context.send_activity(
#                         f"⚠️ Sorry, couldn't find any of the selected software: {', '.join(software_list)}."
#                     )
                    
#         except Exception as e:
#             print(f"Error handling card submission: {e}")
#             await turn_context.send_activity(
#                 "⚠️ Sorry, there was an error processing your request. Please try again."
#             )

#     async def on_members_added_activity(
#         self,
#         members_added: ChannelAccount,
#         turn_context: TurnContext
#     ):
#         for member_added in members_added:
#             if member_added.id != turn_context.activity.recipient.id:
#                 welcome_message = (
#                     "🤖 **Welcome to the Software Assistant Bot!**\n\n"
#                     "I can help you with:\n"
#                     "• 📦 **Software Installation** - Say 'install software' or 'install [app name]'\n"
#                     "• 💻 **CS/IT Questions** - Ask about programming, algorithms, databases, etc.\n"
#                     "• 💬 **General Chat** - Feel free to ask me anything!\n\n"
#                     "Try saying something like:\n"
#                     "- 'Install zoom and slack'\n"
#                     "- 'What is a binary search tree?'\n"
#                     "- 'Show me available software'"
#                 )
#                 await turn_context.send_activity(welcome_message)




from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, ActivityTypes
from intent_parser import parse_intent
from llm import get_llm_response, get_cs_it_response
from db_connector import (
    fetch_all_software,
    fetch_software_by_names,
    get_software_info,
    search_software_fuzzy
    ,
    log_software_request
)
from card_builder import (
    build_software_card,
    build_software_selection_card,
 
)
import os
import asyncio
import sys
import json
import httpx
from groq import Groq
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
 
load_dotenv()
SN_INSTANCE = os.getenv("SN_INSTANCE", "").rstrip("/")
SN_USER = os.getenv("SN_USER")
SN_PASS = os.getenv("SN_PASS")
 
 
 
 
 
class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        # Handle card submissions
        if turn_context.activity.value:
            await self._handle_card_submission(turn_context)
            return
           
        user_msg = turn_context.activity.text or ""
        parsed = parse_intent(user_msg)
 
        if parsed["intent"] == "install":
            await self._handle_install_intent(turn_context, parsed, user_msg)
        elif parsed["intent"] == "cs_it":
            await self._handle_cs_it_intent(turn_context, user_msg)
        else:
            await self._handle_general_intent(turn_context, user_msg)
 
    async def _handle_install_intent(self, turn_context: TurnContext, parsed: dict, user_msg: str):
        """Handle software installation requests"""
        apps = parsed["apps"]
 
        if not apps:  
            catalog = fetch_all_software()
            if not catalog:
                await turn_context.send_activity("⚠️ Sorry, no software available in the catalog.")
                return
           
            await turn_context.send_activity("I can help you install software! Here's what's available:")
            selection_card = build_software_selection_card(catalog)
            await turn_context.send_activity(MessageFactory.attachment(selection_card))
           
        elif len(apps) == 1:
            catalog = fetch_software_by_names(apps)
            if not catalog:
                catalog = search_software_fuzzy(apps[0])
            if not catalog:
                await turn_context.send_activity(
                    f"⚠️ Sorry, I couldn't find '{apps[0]}' in our software catalog. "
                    "Try asking 'install software' to see what's available."
                )
                return
 
            for app, versions in catalog.items():
                await turn_context.send_activity(f"Great! I found {app.title()} for you:")
                card = build_software_card(app, versions)
                await turn_context.send_activity(MessageFactory.attachment(card))
               
        else:
            catalog = fetch_software_by_names(apps)
            if not catalog:
                await turn_context.send_activity(
                    "⚠️ Sorry, I couldn't find any of the requested software in the catalog."
                )
                return
 
            found_apps = list(catalog.keys())
            missing_apps = [app for app in apps if app not in found_apps]
           
            if missing_apps:
                await turn_context.send_activity(
                    f"⚠️ I couldn't find: {', '.join(missing_apps)}. "
                    f"But I found these software options for you:"
                )
            else:
                await turn_context.send_activity("Great! I found all the software you requested:")
 
            for app, versions in catalog.items():
                card = build_software_card(app, versions)
                await turn_context.send_activity(MessageFactory.attachment(card))
 
    async def _handle_cs_it_intent(self, turn_context: TurnContext, user_msg: str):
        """Handle CS/IT related queries"""
        await turn_context.send_activity("🤖 Let me help you with that technical question...")
        reply = get_cs_it_response(user_msg)
        await turn_context.send_activity(reply)
 
    async def _handle_general_intent(self, turn_context: TurnContext, user_msg: str):
        """Handle general conversation"""
        reply = get_llm_response(user_msg)
        await turn_context.send_activity(reply)
 
    # ----------------- FIXED METHODS -----------------
    @staticmethod
    async def extract_incident_data(user_input: str) -> Dict[str, Any]:
        """Extract structured JSON incident data from user input safely."""
        def create_messages(system_msg: str, user_msg: str) -> List[Dict[str, str]]:
            return [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
       
        incident_extraction_system_msg = """You are a ServiceNow incident creation assistant.
        Return ONLY a JSON object with the following fields:
        {
        "short_description": "...",
        "description": "...",
        "category": "...",
        "caller": "Guest"
        }"""
       
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
       
        prompt = f"Analyze this user input and extract incident information in JSON format: \"{user_input}\""
        messages = create_messages(incident_extraction_system_msg, prompt)
       
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=500
        )
       
        response_content = completion.choices[0].message.content.strip()
        print(f"DEBUG - Raw LLM response: {response_content}")  # 👈 log raw response
       
        # Try parsing JSON safely
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            print("⚠️ LLM response was not valid JSON, falling back to default incident data.")
            return {
                "short_description": user_input,
                "description": user_input,
                "category": "Software",
                "caller": "Guest"
            }
 
    @staticmethod
    async def create_incident_direct(incident_data: Dict[str, Any]) -> Optional[Dict]:
        """Create an incident directly in ServiceNow via REST API."""
        try:
            print("🔄 Creating incident via ServiceNow API...")
            url = f"{SN_INSTANCE}/api/now/table/incident"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
 
            if not incident_data.get("caller"):
                incident_data["caller"] = "Guest"
 
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=incident_data, auth=(SN_USER, SN_PASS))
            response.raise_for_status()
            print("✅ Incident created successfully!")
            return response.json()
        except Exception as e:
            print(f"❌ Error creating incident: {e}")
            return None
    # -------------------------------------------------
 
    async def _handle_card_submission(self, turn_context: TurnContext):
        """Handle adaptive card submissions"""
        try:
            card_data = turn_context.activity.value
            action = card_data.get("action", "")
           
            if action == "install":
                app = card_data.get("app", "")
                version = card_data.get("version", "")
               
                if app and version:
                    await turn_context.send_activity(
                        f"🚀 Creating ServiceNow Ticket for Installation of {app.title()} version {version}..."
                    )
                   
                    software_info = get_software_info(app, version)
                    incident_description = f"Installation of {software_info['name']} v{software_info['version']}"
 
                    if incident_description:
                        incident_data = await self.extract_incident_data(incident_description)
                        result = await self.create_incident_direct(incident_data)
                        if result:
                            print(f"DEBUG - Full ServiceNow response: {result}")  # 👈 log full response
 
                            # Try to extract incident number safely
                            incident_number = (
                                result.get("result", {}).get("number")
                                or result.get("number")
                                or "Unknown"
                            )
 
                            print(f"✅ Incident created successfully! Incident Number: {incident_number}")
                            await turn_context.send_activity(
                                f"✅ Incident created successfully! Incident Number: {incident_number}"
                            )
                                                # 📝 LOG THE REQUEST - Add this section

                            if incident_number != "Unknown":
    # Define log fields
                                software_name = app
                                version_name = version
                                status = "Created"
                                timestamp = card_data.get("timestamp", "")

                                # Call updated log function
                                # log_success = log_software_request(
                                #     incident_number,
                                #     software_name,
                                #     version_name,
                                #     status,
                                #     timestamp
                                # )
                                log_success = log_software_request(
                                    incident_number,
                                    software_name,
                                    version_name,
                                    status
                                )


                                if log_success:
                                    print(f"📝 Request logged successfully for incident {incident_number}")
                                else:
                                    print(f"⚠️ Failed to log request for incident {incident_number}")
                            else:
                                print("⚠️ Cannot log request - incident number is unknown")
                        # ----------------------
                        #     if incident_number != "Unknown":
                        #         log_success = log_software_request(incident_number, app)
                        #         if log_success:
                        #             print(f"📝 Request logged successfully for incident {incident_number}")
                        #         else:
                        #             print(f"⚠️ Failed to log request for incident {incident_number}")
                        #     else:
                        #         print("⚠️ Cannot log request - incident number is unknown")
                        #     # END LOGGING SECTION
 
                        else:
                            print("❌ Failed to create incident.")
                            await turn_context.send_activity("❌ Failed to create incident.")
                            # CREATING INCIDENT END
 
 
                           
 
                       
                       
 
                       
                else:
                    await turn_context.send_activity("⚠️ Please select a version to install.")
                   
            elif action == "show_versions":
                selected_software = card_data.get("selected_software", [])
                print(f"DEBUG - Received card_data: {card_data}")
                print(f"DEBUG - Selected software: {selected_software}")
                print(f"DEBUG - Type: {type(selected_software)}")
               
                if not selected_software:
                    await turn_context.send_activity("⚠️ Please select at least one software to install.")
                    return
               
                software_list = []
                if isinstance(selected_software, str):
                    if "," in selected_software:
                        software_list = [s.strip() for s in selected_software.split(",")]
                    else:
                        software_list = [selected_software]
                elif isinstance(selected_software, list):
                    software_list = selected_software
                else:
                    software_list = [str(selected_software)]
               
                print(f"DEBUG - Processed software_list: {software_list}")
               
                if not software_list:
                    await turn_context.send_activity("⚠️ Please select at least one software to install.")
                    return
               
                catalog = fetch_software_by_names(software_list)
                print(f"DEBUG - Catalog found: {catalog}")
               
                if catalog:
                    found_count = len(catalog)
                    selected_count = len(software_list)
                   
                    await turn_context.send_activity(
                        f"Perfect! Found {found_count} out of {selected_count} selected software. "
                        f"Here are the installation options:"
                    )
                   
                    for app, versions in catalog.items():
                        card = build_software_card(app, versions)
                        await turn_context.send_activity(MessageFactory.attachment(card))
                       
                    found_names = [name.lower() for name in catalog.keys()]
                    missing = [name for name in software_list if name.lower() not in found_names]
                    if missing:
                        await turn_context.send_activity(f"⚠️ Couldn't find: {', '.join(missing)}")
                else:
                    await turn_context.send_activity(
                        f"⚠️ Sorry, couldn't find any of the selected software: {', '.join(software_list)}."
                    )
                   
        except Exception as e:
            print(f"Error handling card submission: {e}")
            await turn_context.send_activity(
                "⚠️ Sorry, there was an error processing your request. Please try again."
            )
 
    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                welcome_message = (
                    "🤖 **Welcome to the Software Assistant Bot!**\n\n"
                    "I can help you with:\n"
                    "• 📦 **Software Installation** - Say 'install software' or 'install [app name]'\n"
                    "• 💻 **CS/IT Questions** - Ask about programming, algorithms, databases, etc.\n"
                    "• 💬 **General Chat** - Feel free to ask me anything!\n\n"
                    "Try saying something like:\n"
                    "- 'Install zoom and slack'\n"
                    "- 'What is a binary search tree?'\n"
                    "- 'Show me available software'"
                )
                await turn_context.send_activity(welcome_message)