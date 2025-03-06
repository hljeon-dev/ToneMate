import os
import gradio as gr
import extract_rgb_utils
import langchain_retriever_utils
import requests
from dotenv import load_dotenv
from PIL import Image
import json
import urllib.request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials


def define_color():
    if '봄 웜 브라이트' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_HghwDIKVuwPDUsfXI2g9iWvjmaqYwfSJr-Q9HiIbVCZRgxAN5UIINR4ySdbtAEtLntQPSx4A0LvmwCx6PTSZoyIEeNgj00mpdsz5bHoDnLgcvOd3rf0CrCDUpoj-ZZmCVE_MU4CRpNvDX0E5tKDcNt8GbVszCso9l7fkgQoODyCWQjWNKLVE2QVfvKJs99sauC1wBaCAm_QvsWktUKhBV0aF9_DXplvBKw6GCovdbC_3mSyAVcQu7W5IbiLFPGj3OipSZOypRWBgZQTT4Og0tHINV3nkPk4iUKFuZPBfupCCKHbnmARmP92dBnGq67oDpOYkozwzJKtEv0FcmFgiz-HsZDmbiaKjzzyQ27EgUlSkRx8M-fayj0bLKVCVm_LhRi6FsYbkbO1hB5ik_BFEs-sbH27A2Pv6NZ4i2iaTS35ASvKJ8JEp_w2hBx77f5svQEH-Y5xQ0MUkE_yBVSaBSWfOYwVbs6HNTuWf3QZFmB95He3j9_VUZ89V3PbPQWFt1kPec4KmV9JGsMtZbTTU4up7VyCq-sNdmWO3BA5PoSSe0cfx0dZHIx-SxxAbqxJeC7IiTvI_figDbfBGVe3hcsRdbcE41iYrSZXGbYn_hpWVPmtHgI533suIfw8cVtDzIETTaB6VF8yRSxrCwAGRFc0RrPjz26_e5h-1yh75mye4ijIx1yJ8mYeQT2wRnHcbKW9XvavZ1jDILPkGyYP-JaHzhNr3ULMqY__jQ37_l14bImEKZuD8h7Q-HjkK-pKA4BnBwXy2x9CT5xyLRIsN491MuHJ4Cp69NlJP6L2tGddeDk8TSQf8RaZvBNaK-n34-Cfc4HmDQLJuvXqwWF_dt7MykaTH9eTrdO8rvYNmchvNqtwltjbiNjbb0F-VQmj4Kixhlv_Sq2ulDLp43MMVZyOJCUMMs1qqoBtSw-L63rb31okMZ-wDdYwKoe9Juec-N1ipWRAg7pVzqrlOu0zu-ShUOFflw5dfGLeJhrzVKbZBJ3iPWzVSYjnpVXPG-0xysjMM-uMb05x_2O4YOAcM-lIN--6F4Di66nzYJTksKG4Vpguti2UDs2G-ue-g3NyB26VlH0cqd_svbTQhJOuc1pVWuCRWi_CoU-llTkyh_qVa-QJLd9R--NqiBwmWHmd_5idu0Db_GRM1JdgNvX9c9B60UekTU8Qx0MVOQSlayD4KUSrtLtCaOhiKe8-_6SyqMrxSoGcx5PwOUNoowYbOvLgFjPLC-yqNC2avCfF2BWA3nA7U8K3hA-0gQXARcdJAaPKCZnDOMmBGgWiDlZJMUleATMOR7ELTkrc81Yt3qyX4-fGcNNt5hVgMzrmELXtrRyH6nVBX8bBMiUMd8nvFKDnSM2l0Aoax3LGCkxpLntswW0OLQviwK8Yre3_YcUI5g55kPw-AKm_GJw_bR64OFy5Ba9ueVpe9ni7l21MBEKHpHejaAW52QBi30XwW-W3cqios5yFgkHGJqmRnOYmsOJo0hLJOn9O-Mxdbpg-cjQ039gTE6VFBhDEGikSnNWkegGah5MnXxlvhJPY1wf-yWwwnkn5oHkkeoOs-NR005Y8UBFkDTg72s8w9XnRAfblVV7W7KoS33_stErfQ_Rk9Bl3a2moaSZRsXu2ujz3FxtRxY539qZm8ho2mNhDwUwZ0YerUyPs52PXyENKMCoVf2OINERH1a47q2ZFrwdgfhj7swRxfdVXj5cnqmr5Cl1QBqQYzzbogNMETa0EojRopcqh46OXxzeHisSz3U=w2994-h1616'
        return garment
    elif '봄 웜 라이트' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_Hf8priIfsL0ores43ww594KQwu_4seekqLmkxNRcOmK3XedmHMLw7ZhWRirF0nQH4FS50G21SIyvYKNB68A0hhYrrhN3GCneGhXSuQh8Pr2HwFvQIVCRJFJUB6sICqEXRXnV0pnigQuxzJYtAD_0zUO-_7ce_60V4vMHzG7j9eAEFnQo1BeBB_W4zPINbl9R6Hjd_smlry5IGPgiOjcHWGrhWHOZUhNoCsTkJKSmL8PIhOa5zN0tWUSGLdqh-dLY1rmKOCUByXFj3ZdVcmFHDJ-c5mSUNJlh8aNYD10nVNGwZtufghPwh7154snKzlp2PCAYkk8gqQDFsDsnW4lL3MLkMhURkpHLau9JpoKQ9_69ic5AOIwyQZU4J_I5HhKW_tMp9V-320eVAQGkrtAEV23u1DQsmhNraQy6d5G7NdJlh2IolpUhFf80NROjEKngF6oiIaZHU84JGX-VWmZS6pkdF-LDvG_JvrLrx3p3-A_pJoeeko3YWgjJxqelz9sA-QAzYwC5Kv_J-JflIxuprgLO8XQsReynY1dtC9lyBTMA-wwisH3pQ8WrMEioeZcf2rvrcZX7K18rBK_D0j53pYNK8B8nHy4mvjidi8u9s3S3ZmoSLdL2OBtaX_sijwQQHi3DtPicpFNhHjFDsf3ENYb-TKnFDHxfMHu7lQtPiAnb1NQ-mXkwb9DDSwSRVL8G_AbCt9gaSXb6D_0k1UxZM95wFY7-bnm7qxKt5gbvN0qM3zZRxzUVcwDwNWDvRjwHvHWi3GDUhIviD5-D1MaH1laMvYpcSwA5Hpmi1HlZZALLsHUeXe1NFYC2nwwZ6QQ-97QFXdS6RUjm7BGbo862zVDbMV_QvkkNlWLr8Sspiuy-PPTkUooE6eHObhuQEN3sh5rDlHEjtIlZiTFXB4sCwvsJSWwKuTRus7zjJXXgDcLin1_xlpcWWrOl3W0_FYm3asw_q8j_rrib81oS8m7zjTdYrXC3jyTgCw-sO-eUlNlo_SMks9QKbceOrcHh-M1xn-q0dnWkLoHo7utP0k-0tiFeGCAV4jAd6Whczx7ub73e82ALlz5Qh4znJAueyfq4oOoWxI0yaS_bYx-0kuD4vE9pjtAEXdaNVwLX3jNB_Cqj--j4mgZ4UevtVtiAcyKtqlL5OEh_BMT3lOR4SMhH06WlZ_AGMWw9VDrygh5Lql_Qe_fKeK_9OSoXzpBymkzFuIIrO1xNlA8ndGfnYzNYQnTv1rqu_wh_oi6_6Jh6OMDvj8eGaum6j6C-5u-jQeQ9SwM8Du_f8Sb15k_uiOP0nuzOTIvEDRmX8FOGI46J2gw3T5v68mlKTM2L69MAwmJlJ9qYQmJ6G7bmlkRWafbZijzIMa3vCHbEk40LfODfCkGiIsuBS0IK0OaFhzSaxl7BiuNM1vEMrdDJ-0G4aWK59cOJO3mmzs5DvME4h_Rf2sb8tvRoeo9W9HKEhAPDMsnbCdKLi-LlGscrnx-8U64LOHzzHZCfbHUZfvTW36aj5k2dmNU-98mgSNOj_GRkiRqI-EgXcnk4MYggk3A6Hbllq0_SUh8wIyiBrIYSDVuq7JtDO7fW8iQZvywd4FnRogmEibWoaoFkVpqau7MdwS8iIIWnFyxbWvy6sJmNl-JWTrR_7vXbFpOJ6Aeo0ppAvxaQ2gCMWtyH2ek9NHbtDgacVlA-zarxWx0zJ59Bg_SA6QtGKWPH1Ym0OtA6guR4CHsqC9cWV-7O-QumsrRSA5gPC6SA9gGdXiJo3a1S8=w2994-h1616'
        return garment
    elif '여름 쿨 라이트' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_EOzOyZ4Y9K0kxttTOjQ5QyaYTZE3bSDhaKDymzstH4_ycnVosqgmf86vO3ppj247HgGPkTDRwPACing5NUWQCCeneaibzHixfhlgm4Bic6m7sRFqtyLUA32xJfyYz-aPypkjjdRmfNjol75FjjnOLMtDAlL2owrLpxuDRUTe5o90BBxNWP3A26lC4t4jAlQ61agymMlWjldYU7moMMWHeQas388rtRmxhOVOSPbmZ9B3CqwWheNDllKtxO6d-SaQ1tMHQWy2Ay_7EOSqXukEiJFYL-T2U54qSEkmOR0rPplzQNc_c4GDgLNLaoYIZUa6Sqmas4ASTaA7BEUYgOngh7lfYXBhqL3lMMBxK1XAnF0cYGJiO1GKCK0W-kjhUp4EMnNaaqJReWJ7r2ox3u3mm0gtV3yuUMCW-VwnikjLBKrN2dF7GBspMqiNsr5Ygzk8GTSVdXbB4Z_fycDrn7gHm1zkTcOd-n3cquDoXcMCJdp1MT-ikj-93GfwH-7_9O59vOEtfuul5Wflc5XFY89xzuOfmigjgEVmAQ6ZtrpLvrdl1444mepaw6nhFBmFiZ6oNGD3HioZHUWuqFSzBdZ8vwwt5wU9X2wyCCv1zzZbotl4mcMVb1WnAlvVjcPTtt97K6G-tzTHPuz7k2nVlaO9LyCZwH8AuCeofOxDrE2Nz5_gftjEPVHZbPtYLiFN7u6KcD6Kumd7Zt7UhZH7tPQVk41yazNKW9Mr635xlVFbFS4CsdUpd5EcpM8SDKYFiAWjnVLjWxvW5wAG23EaXV0RzXDy1bX4jm2soyi72MmA_RIiG7RYW3ybE8NNvChH-zxSGaZmPge7_dnfWTEb9rYsGAaHu8sOMEtiVn_Ut_CUK5JVW2pMNExxzxmCVe2HLU6PPkYRbqlvyW0EIouB-OHPVsBu66Urd6XyiRqF2ApbdP63bpfKmq8w7MPa_325VvcgU2xtxjZF_ZjpGEnt8YGAmkfL5KrjA_CAwNqLJxzT20BLJdw7MoD0iZeARNlwK1y-CpQ1IRyJjWI-McyMhMfxmZiEv8wvUrcMrl6B5HJga__zlmdXzQsWp_y_0HP5zzaT6Ovyckz9cTqirynmzE9BrVwoZK_rzR-mY946G--QlWJCJ7ZM9uU5pfB7UQpKN4zmpHRu9icKuKhy5_4BADdV-qEOWHU87x37ysAbwxvh6NdzTOHqrh-aZW-__XjfuaVUsbBjULy4vqhQTwab5cIS3ekpcac7KgT1f_4ElIiT19HCwyz1rbrAulOBExc3RmUsVjlXdtOWgIQ7R19VeDuMxZrslqw04GOtF80QNkyAvPYUmN1TzIanq7q4iGPVevRbISRdTr5ogDb6pu9zzc_Y7_dwkC6ljfoMoA9yGYw_KIrbkvyRHMcQoiwlsvraBDNN6q6p5epx1Tamx98WRxwT3yXXjWTw3yrFPJ9k7MS-vrSAVEo9mImU7J1lr9Ke258Z_TaWgWb6ZG-PaP9-eF5n-7t6rLW2wtvXMH5vpF9sG1hVR-i4VNRcSp1lC2d1UgGaz56uWs2fryq_hLAcYfcDJ7F3CQ3dbmh9ExThyLSLvAYG_DiqBbY4mz4KptkNKGdLbAlHYU2oNu8KfZeeZ6AwX49xHaIbgcDmPJWUZjb-aSm-AixzN737UnvAJJUcBtyfQ-MVYm-6j2-8IUaHCVm8xCBTrlCjStZkfA4nfth21vfaOVlaz83rjzWD0Fy0slQ4qh9EceBDF9NhUOi6jCArDcNWg16j-_eTYApis=w2994-h1616'
        return garment
    elif '여름 쿨 뮤트' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_FyfTehdyGsy8ASMIzXuKys9TAUAYJCSN55kn3mvMhpHP_sHNRH2H0qiMqoI_Sb95_RXS6Eojdaw1aLp1JqoTsMegegvIfDWMaHUhvGJ1aayUJywscKJBpG0iOnShJp9-MauSK49d9Y-fLywjSV464uOVw_XpMgk9LJmxkaY6AwDIZZZGp1MLbm4jt8H4fazH9_Sfj5Em9rqlRhhKAAkVWgvoJDrRlZqoX0apN1LLD6TLs06L6mP2bDSJdQNBCUtT9eN__Sc3-eN27BH0IlcsiYtn-EPkjMYXRZqAUCx-iZPKoafO3q30b-AsqH-IYr4jRfoW094jvmh09tkTc8hbIDZ0936P_8L3yl1122-lePnUV52jvrmuzjaU-apyEGGf8BXQ_j-3emQr3RJetFanRvjfl-2EXW3hLE7JaPV12cZZnKedKK77MylJ2cm1N7sz2PEB7du8waD6PkzVf1czX4IvmS6CTZhqf4oCsLfTIlQCRUPP7Qc7eB0qj34YbEu3mqtpm0ZmtdB0RhgiCnsXPzaFdZ3PbZUkbApaL_X2uoSaJX4l3JVkHrOegaWc3rFt5P5tdp6wXYbT1jqAdmByTcBnWwe3noZafYVoDIun_6gOCP2kBZRwhJUuz0aA_CdiXeRbaZqZXq2BmhyqZ_35F215E0wPTRAbNlWhpTwJyDHiPoQOuWTYwJ2vnK63PrF36PRzYAfpCqEo5FMhWdSSn4DECGbInopveo3h4JhPLyaOg1mHlZbOkr8yzRpxJWAl4dl-Pu-GjGkjd7qZrRnSwBFwIQF046cF_ZhAtn8dhAI4uz34Cem6dkxU8qJDQBLcWJNFvTM825joG8obFCJqP3oGRLqaip6RoVYnycpN4PBBE5d3gWw_8rI-mWEu1TKg77jKGXzZT8Wi88ihyGl1_c8bo4-VCloSJt11HIs71HflfDFWejvUR38jewJ-akjm-HoKbPq_cSxP1rhYXskQG2z2y3MJ9njwQut7TT22dYOb6D9Kn6yt35zJ-s-Jj-TvKoyVId7J8q8psGruhn4FbpIDgcJm9KMnYPi9lYJofCkjzR5RLvYYxX04srXo2MGTmTozR3nv4AYk_bdvH2KmsFD3lb52tbJi8wrEM3GXJXdNR4kp5wO3-R1j2d1lfhlJ3CSZni_uVd5wm6WBetGUYm7gPnXSaud7aiFKSYjeNh9t66FTU2jaStUaNQ0s6cLd6lonKGmTzLBokzlmmvt2r1L3j95GCnYHH6OHS-NdCU01fCXjReuVrHBmcI3TELKiRmLtUeJaFoLfmhfpaIsw1czeRb1XAlDa-1-bamnb25AwaA99K3iSZtbWx7GBak3tyq4ciHuLeDRXWf1ny1EQ7jGvzCoboAGXWN9xazjBYmflurrKX97YYtzgIeJpRDcRDOQMqMjJgIxxKniJht72EOybXR2MhzsnDXqEwcL0pPuSKxnbqAtQnBUNOu-GlldyVzWYd6-PhztC1F2bt1dPoUv8O-iEb-8eD99BqIc75k1q1_TRFwjkKi02c5I9eIVpaLpzGCH5BLTg3MyjRzqI2aFmo0ITe6K-y-MAq9LQK1P4u5qSPd5vJF75C5TSiH76SSmKUokb1Dypapt-ebtxoxoAYFaZbY9MCuImEqsZ6hUl7qnxi4enMYBJVBbiOj5zGDCdMZZ51uIxKNeVeCCYUrKTal4bXZRJQtTICPFCT3aj-RtJPSuk9Lf9keicAOAqCnK_HEfMZ84z1nnGCO9fxVD8WPNnbXJQUe8e0=w2994-h1616'
        return garment
    elif '가을 웜 뮤트' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_FCSCNEgmvV14eC4x3Cz0xKsgypJA9YsaHcDVJj38S0ShG2asBziwTRQXP4JmQK0qamIpE1hiyrnmJiXLfrlkWDL2uz8j4tiwYzBVGaoHdtLYbacMnb0I2YJulejCvm1bJMbUXgjavYbW6rBiY5gN95kKU-2TzPKsX8OrZMecu5kuCB7FtyohvzF0w3wdp-pJQlJyV-sF4wmdYWY_pow9aTrh8RJz_NlvGGEe8thzo4inHFqj9ZOltS50VGx4Aerh5xBSlBJlcjTCTLBfCHytL5YtOnUaeWmsnnCuwIM2q96zo_r2hi6EL1VppiDXY4kMCCNYG-9pW3gO37s3_fntsYZ-y1FGQN-ELsPv4jaX88SHTANb_mKcCuXsnqDkg4nV4MWN273ZMNeO6CzXRNm4JfJxguTBcIS77uJHBPkRNDc_MbHCxCf23PhOHxiHl8t9Tc6kT2G5DBVCSecPtgIIQ-4rsBAiZg8Hj_UPA7iNS0XGluSqHKnZEhjcLFsWPX-CXFGVlWUTNz2L0KzIRiRMjd_sZFMgwpeUbxQp1jbiWc6JWF5QB4BYuz0XKFTo_sOlxHwrGVGm18py7-QgvddBowpyI5Bo9F9Ill_cK0o2tcz-zKgXMIcjqe7EMINIfQ7_cLChKp5C4P09b_7_Jp-EZz-FwjV0tfa8QITU0pDxL8gRXLTULVEIyNeiC3ZhaO-Hb8OnNBFqTLVdVCCXAB8WKsE9CIMy-NsdD5fwQl3T7vyEsqCyZIdcfZAXjrV7tjp7xX03OmDemrteOetuxCJnAl6xVKN3vC1rnhtr8pKGz9P3UxLSZEBPiDwtdtG0MxmldwXxDkzHx5VsICI-MR7N79HPf5NM33SHRAlFjT80AcWDbe8RJH-SanlR4va1CsFi2KMpN5OWkW7KDrJpydeZt-4-fetfaAHgKss_6RIXxEQ2Pyyc2VLa8MH7fWCX5rJ4W6jeyT5aEyEM3lvBERkfVo1O7C11qUp7BhjOir3QcnWqaYs4TVRmQOE6b5j29tp9lulg8OyDtY5dwGTRcgkdiqbj9Don-6vgFCSL3NIJFmGVuB7t48MNyrZk0o70MABlGRG99JLhpmA_Vd0UwO_ACP8QcBxOO8CVdkt6KcUhFtaxfauu6S2_wIubFRu5Ydj0fQ4Myh65hSWnFeR6IEOiDBcdPhrXCbPyLIX7iLR1SrX02TMIZVmOyNygzYzQVorI01_pr3_hUp4nIZ_LilIyObO1bgCeKjPSLwFQknPFuUSrs_BKfdBlYA-YVC9DtygThx7OBxE3cZYU7wzJjkO94etWSEKIfDCZ2APZID-kUbIiRJw1JSCrWuM9uypp96jyFu-eueN_P8qwfYq7FjJ3LXj5wx1v2uQNCbtDzN6_yxUwyYhXSs9H1sgc6I2FkP9CYE8Ebgcg5PVshjC3KRvr6b_xeUUUVrbxgwN-7pHOtD4u6Z8aDURmR5vaTo5oD5-Ov4R16yZzCIlRIbmkvmgKMQvlrBeUVFLBxTZQzXCMRt3xooTBw8x3y1Zq_2AaIwk11bHIWoQWzIuBBfepAuPMxFPk4ZWMZz96BfMiuJc9SL_e5Q4-s-I07NBJ6vZd70UqulFZtYZbQcpqxQgManhDNMK18MS-EJyn41XpLaPyDMlNsVoSIQbpyEfdsGeh3qy6YGxSip_hp69FVBPZr0q7ray4Ew3sRm0ewVMw18THJuzQ72Tt6RqWjLMeAqjRa59LGsViv3LGDS1BJ3rpa7hRzzflhqc58CZ7E2fT8=w2994-h1616'
        return garment
    elif '가을 웜 딥' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_FdhNiQVpqPLB4KXpXT8WU0GV8BwbTtJhh6jMRi7-yBfAucYO-7UEzuFR4eP-l5lDTBtNHLaR_sc8-Tl9uV1xAcmpEs29mCKPnTJ1b6NITXcIFrAcEefqpFzQiB8uV_CMpc36K03F4c-5ZXsvN5KsZh9ihlLlzO46QGH1hIyz8QK3Gmayw25YDwqzOx5N18DnFNkTK4_uFe27ME0Ca0WrAEoFT3rVyKprwKUWEWxV4VLAt_kMF8tgEXF0vaoKS6JkGXHnvLNAt0IalOkbupABSY35-jC5H1I8PYO6tpbKliz5XHGR0Y-lLU6WlhEUhLs7L6igYE_GJUXr13tH883DW4tUzfRGp0VjpACzX0UvzuzKrBLa6GrJOIkAVvVUKO5CF64rAXGFIT5Bs_3TzF_t33N2-9bInYlAuExXWp1s_qqC4jM56TcZGgtF2BQVXe-oMP9dLg6sBZgd11ELW6dpnJLgWIp7IoCCW0bB9Xehn2FXd5mPTw2MzXZ_cyzTQJ9G6ouPAj85JsOx6oS6HnAqjaZ8jBjhVLJYGPZzSZZE2gOVtwhYe4q6abWjOlwzjjrvKuSiIYmua7be9Etl8Z6oFbMEkTPzfUxp1Zgiqkbo8cZ64XEkqHmAIA7JStYP3UnpCe2cyifxmdxD7OoyVpzb3FBu5Hq23afc_6BfvK0nI0u0JEtRMD0NitwHLrEY153Q9lvg04bW141VBB_uYx1kw47ZdFF6V8kBt55JElWVG0jJYNduXURMgkKMECdWpiimeOZKbFKsrPdLVoTLxtZ-FkwBLxGpYKeM60XF29pvazv214G4bWUyOxqCtDGC_Efqy2xMIT2rQisLaF2NqvFXqseSVEoBvZRKb6yZawjn7iOgRwdoMm6pt2RIBu6MR6iEf253bzeyzTJQfog-HA861SnTKZJNLd1kQ8MqjK6zJvjmeNcLiFHvRrXxEzkc8pBD6eEMGAaChITdWAye5FY6_HaVX-nNzNIHaVBT2zZjIaawwxCj9ZWsXLOG5WW8VvQxn863u2ffQkySqcPw3HclfIc4BiQ3PLyhnjrUXqNru7dJK2H4NK0x_KfVmaaRYV9qWj4dLdChXf3h9k7NTWOKqRSwlKCK3XoBSESAoX8NLsXC0t79UzdI9amMkJV8YrBucK_7Iy4reJMDrvpZfvK6bty80ayYoiQABYYej281xp5MqEg5mdZL1u34efy1VvtL2RPWZfOsSxThmFdirSJOJ_nj-RagzSeiJISNr3VqPc0Dv3KxoCHpMSzIK9Le-GkVd1-Zgh9iWHfsxOwdjcsY6VX4gSxJzaNG8VjeGtsiAi_v6hwrlhVP-YyiEh0O-9MnpfGOobBt1X-M6-44kopZ8r6yxzo228GKk7OsGpLjhU15bxgpvyQPFx6APmlGxdc8-fdjtiZs6EgBZJbOLnLWBqV55txPw4cnC0nRmoOyRFLDxVTPPdUEwUm6G2WFT9we8fjZDncToXpf4fNdHojBQV3Th1RVGQuNWPO6ruEq7esszRMJr1wO0TGTQP3N2i-Ed7P1rQ0l9eiwwd4CJt6XkfBnfe82I7NbLlkpYBNGwPrZWNeex_FKP62ti24JVXDoSABm8tVz7vBljccMGiP_UMyK2k-6CDNI6jvec6khTdbD4smcV-ashh9JLjjy-ScJp2K3UfU0TVClhDch71SmJpeav9547MsXYza1F8U1Ju1r_4XVgAtYjN1hEjEmr7bHhOt_VXJtc9EpDAlNjonjWEbBOdUFmfOcGLlgE=w2994-h1616'
        return garment
    elif '겨울 쿨 브라이트' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_FR9NGl9_glrKhG0WG8JDr2sb4bvi-XiO8hOziWNMiZEn5j1ld3MeVvSwOwWGXjrfrhIrSJp9Fgtcso9DcUIyP8IfeFILmqsAtmCJI5oFCz0pQiGzIFw9gqNJgKoItKZyk6O-O7-2z8TUmJRRLmWqAVen0KOpR4fvfKaAnEvAi4luhOID0YqbYn5a55XlZNiiFAewyWHjQMQXhuBpkPHluqqBxxP-_h71wzjn5kEgQbMm7t6nQvf9pmbkRzFIUwio4YnztxxXHuZ0vLCqvY0SB0z030Qxb0qp4aQqiFl9r-d3m8XWcrxI6TiSuZI14flKHTGPFVOS1RmwNFpzRZYvIVcWLr1gNqLL-Pt15WHz5exnbUWsFQTsFqv3h9-_f8R8Q0wLYL276o3TpkNsb_dxVQBKapB1CCcuQAlaRAjJcjCN1aUfXFEh3WW5pWU19Ow1n7T-SZQou2qsjjpPk4W4thhqaCJ5anpQNV9YMjMNd9Za7wUGKXko6IYLIponv-Z5k7JiobNLXmBgFLKB3eCHNj6FWcQi_HU0q1eazx1vWu1W9DHUN4Q9n2aV9lzkdl1_ugXRLc4pkkIilEp6RKczixRxUO41Z3BrunZBpUxQr2Ehg4JqdFCOeOr7mxVHqzVLpLBZ_MD9rxdVrKkUOE_qPWCoE6Q9EjlVS-Ys6flmiRcEYAGo3mlgM9rNgJ0Zm8wj_K_l6OctoxZ44wM0zG3pmwaDVqnCEodgjQqAI2rYMylvvyeyd5hadDsv6RwHW_6k522fiZdbFT2ReIusVnNMbZMEqGazra-WKqqN7C2JjPSTfpC-kdVJxYBO-V1vFwbtVHNpKtq6NvpkGAfqX89I-KqEGTqBOZiYwCuhZYsE9yQa_YXvv0-NFfogU5S2RysObImqNYlve7YIWzoAvpogw0dgvLD7KyxszAVr9bmmVfM1zKsgFEKGNYu7e4jMWEUveGQwqpCJbKDi4T-reqXzQKjwsb57szWDjp4k3VUF4bUPt8tDMvdD5t8-j7BkoYhviXPtd6pfZ05yfUIl1ua1JCi0-GmmfYRNedVQ8hyBg6tzb5sSWRXtCvTNUzK7FST4lvDCiJPG87G4y0HylwxVsgL3N2qe38sOBAwavw412ADK2j0czfb6dAiYse5xTNp7FF_pCjQISmkH0MskCabNBta3KPBZsx8Yj5jlNQ6628tQsyxTcPXql9_9ARPSx62wUDvoFk052FFTzgtXdzmKZhYKiG_uX1V_tX8_Ke7c3IrI-uiw_ukYPBN3VkNPHjnWwFrKODwlorpbblBSW3EzqToGsN3hrf3GUopG0DX5LKHwpZUyHocWUNvyNtkZ-VqXuD6HLkdkCdaWlgPNQiuLeXVSiR7POJwgQpkaC54nZZHQcAkfRk0J8Ty1Zgc7OSWUR3nZMZXr_9QjbglGjBkfMNb8iTd5jtcaTMmQxmmIFnMLswukAtsS_qE-JqmCqIgsIsEVyQNF58b0exI1lffmvoq4cvKgl_XXEf89H_aROS0MsOswV1TG6rITuRXBDhMtDZ9WBvcHWZpUD6EHq1Y8uCO8xEGsfK9CzUPQPysNCXbJ2L3vV3gHQpDZ3MaqCQ2fhXjKu37rLD_Z0Njb6gpb5J62q4aYKC_z7xGWfxeZHpcMOv71olxDDK6xElXgEaWcmarIhHwATCR45wLmxV5JlgrE2Mqw1-gVB09Bb__6eXXJAU2aaMn16cC8dt3DYr3e0tbVYY7yqdb7ej0PnR_jKB77QcF1okifyBCKc=w2994-h1616'
        return garment
    elif '겨울 쿨 딥' in result_response:
        garment = 'https://lh3.googleusercontent.com/fife/ALs6j_EvK8ErdCY622bt5a4u02uW25f1TROiA7BBqXFhIOHPdA9QwMVbTqcIVV2P8iPm0ioQ9UmToN6zRKR08--_Yn1YJ8BsXuDOpLQWsnUd0euPx9GHkfhBMULBC0BHy2mSQmyWBCYy1ruZjTvB52ulRTivi5btht1e7OHGyxZUyjFQlUB7MtopIx8kzYecBlkiYCdE-jOn4W2mVjAa6JaZETTJjFGhfpZ3zBe25BB5GBS_ytLyaXQZ5tmuQfInzN0GEknTu5xxLjnB7KaqEblB39PCsa6Wiwvl2o2AFZs56VdNfcSt2Zu2iGw7rCcYoNholNkJN7k0oFEB0CZrkPEvibFPhaJQHLWpdssvx25pwgBuqR0BOunG35smyu-G270IZhynT5F-sN-NsSM9G1c_9CL8MRL8p5_FVhIfgY0NuvxZYfnToxpn_iO5H0H9Fbxt0LyGIT4cNk1rJ_uS3Kiw3MpRL551B-Pp-WATltSWgEjh0NmnwgpFMqAcV3ua5ocallkBRkKLhOc26HT7I7kDTzOAh6Hj7KaHO4-i58K3qn3Dv4uR1D_5DtJgy_86WjRV41e-cb0cokUMnouEWoXXw360a-vyj9vbIMHegyXJBSonRIylFyxjfaq5lO4Rjnx0Rf4J3GbYtr13FOgfwcSKoDMiuKYZDwwws5FpN83u9RZ3d_XM6nAhhEaSIl28X9ZsgjBgdWx_tZ0VEWs20GzjWW4wc0YN67LMpJwm3b5sZ662r7tRmyXN4mNkvWRQDVjgPVS-H1pcKDr7qH8ca9ulC59k8lmCzv6oHLmrBZPTaHfp3MIOwUMq0usdP9Nsn0cVys4cdgNYPlSYaBPhhfez1UQ_6XTpyK5oy7j8kht_ge6DSjomYipg3lBm542in12Y2CjBB6-XoDNgzJlkugwKY9lqwuK3BKIsbSSmjvjFwtsGORhgz-OFh2IUg0kr-Lhm48_w1H34cRltQ0pr_5o0-RTcrWeYYRP_E7NGyYf4ZpNBRnWZjhfLV2DhkTr7J5gYkJnUunVaPPiBV8ujtQMzQhOhOmSV9tIVUGN7FlBi_v_-9TPa0x2gXMZc03022ymhiA_gAC3B2fhfiYBXEvrvKC3fU8puGfRS8dVY4gRcigVEl_99_VMhY26pJaJcwBYuqplbd_xNbBiZ65y9c9EfAa_r_5Wktdd5QhNHIqju0jQmv9AHYBodVlKPO0gvXVPmnkAi1q1zpT0gYGuExvOw2DpdnM25P27UzhpXoeQovANRgjc9-751BimhIAznJQpnwd6ypon7jd-SmBo_0AQQuAhRotf_s3brKL3e7AjUXHQY2vDwWhXlzVNZ0RIgB1CI52LUdVnFXN5nhxS4Blwywq1kc8D9s0l-q11hoTs8BbrVS0OwLMQuSegQMbHzYZYDqfZuM4dpFJ4sQkuxMxZQoqVbQhVVJ9ty7Zo8ftyuKCsNV8zpr1_IsqtInPG-hQy5cE9EgSZ6OMZMJkuo0Oclh6ksNYyceDqd8aJ95IwPbcEVOIHBMjskPXwyvSK4l5Y-vjYyz24APlyMtgbUECUNC2fUwCYMFRqLeYYsVbHo7Q0Nh-hvhtb5NdZX496v0LhF0I_VV_w1Prlar0R2u69YV0mRsZdHSQWI1pHOx7gmCTGbBSGkYyQd1kWbZtBu3HdUWUrHw-hXJq2o11d9sV2RA0MtT_TPEO71qjmEB4H54B7-718R8cWZulaGImpBcBaWfgXn9-EJxAdVU_3o_lugi--qhh9XpCKRSEzjxA=w2994-h1616'
        return garment
    else:
        return 0


def recolor_clothes(person, garment):
    load_dotenv()
    X_API_KEY = os.getenv("X_API_KEY")

    url = "https://api.developer.pixelcut.ai/v1/try-on"

    payload = json.dumps({
        "person_image_url": person,
        "garment_image_url": garment
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-KEY': X_API_KEY
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()  # JSON으로 변환
    result_url = response_data.get("result_url")  # "result_url" 값 추출

    return result_url


# Google Drive API 인증 설정
def authenticate_google_drive():
    """
    Google Drive API 인증을 수행합니다.
    service_account.json 파일이 필요합니다.
    """
    creds = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds)
    return service

# Google Drive에 이미지 업로드
def upload_to_drive(file_path, service):
    file_metadata = {"name": os.path.basename(file_path), "parents": ["root"]}
    media = MediaFileUpload(file_path, mimetype="image/png")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = file.get("id")

    # 파일 공유 설정 변경
    permission = {"type": "anyone", "role": "reader"}
    service.permissions().create(fileId=file_id, body=permission).execute()

    # 공유 링크 생성
    share_link = f"https://drive.google.com/uc?export=view&id={file_id}"
    print(share_link)
    return share_link


def process_image(image):
    # Gradio에서 제공하는 비디오 데이터를 처리
    format_image = Image.fromarray(image)

    image_path = "./data/input_image.jpg"
    format_image.save(image_path)

    service = authenticate_google_drive()
    link = upload_to_drive(image_path, service)

    iris, eyebrow, lip, face_skin = extract_rgb_utils.analyze_face_colors_with_white_balance(image_path)

    system_input = (f"당신은 퍼스널 컬러 전문가입니다. "
                    f"눈동자: {iris}, 눈썹: {eyebrow}, 입술: {lip}, 피부: {face_skin} 색 정보를 바탕으로 퍼스널 컬러를 진단하고, 그에 대한 상세하고 유익한 조언을 제공하는 역할을 맡습니다. "
                    f"사용자가 퍼스널 컬러를 잘 모를 수도 있으니, 반드시 친절하고 쉬운 언어로 설명하세요. 여러분이라고 하지 마세요."
                    f"진단 과정에서 색상을 설명할 때 RGB 값 등 기술적인 용어를 사용하지 말고, 색감과 이미지를 떠올릴 수 있는 친근한 언어로 표현하세요."
                    f"어려운 용어가 등장하면 반드시 풀어서 설명하고, 답변은 항상 진단의 느낌을 유지하며 전문가다운 신뢰감을 줄 수 있도록 작성하세요."
                    f"다음은 사용자의 퍼스널 컬러 진단에서 포함해야 할 주요 항목입니다: 1. 퍼스널 컬러 유형과 특징 2. 추천 색상과 피해야 할 색상 3. 스타일링 가이드 4. 머리색 추천 5. 추천 액세서리"
                    f"답변은 사용자에게 꼭 맞는 맞춤형 진단으로 작성하고, 따뜻하고 격려하는 태도를 유지하세요. 사용자가 자신의 매력을 더 잘 이해하고, 이를 활용할 수 있도록 돕는 것을 목표로 하세요."
                    f"퍼스널 컬러 종류는 봄 웜 라이트, 봄 웜 브라이트, 여름 쿨 뮤트, 여름 쿨 라이트, 가을 웜 뮤트, 가을 웜 다크, 겨울 쿨 뮤트, 겨울 쿨 다크 중에서 하나로 출력해주세요.")

    # 채팅에 사용할 거대언어모델(LLM) 선택
    llm = langchain_retriever_utils.chat_llm()

    global result_response
    result_response = langchain_retriever_utils.result_qna(llm, system_input)

    garment_url = define_color()

    result_image = recolor_clothes(person=link, garment=garment_url)

    result_image_path = "./data/input_image.jpg"

    urllib.request.urlretrieve(result_image, result_image_path)

    return Image.open(result_image_path)


def color_type(result_response, gender):
    if gender == "male":
        if "봄 웜 브라이트" in result_response:
            personal_type = "저는 봄 웜 브라이트 타입의 남성 입니다."
        elif "봄 웜 라이트" in result_response:
            personal_type = "저는 봄 웜 라이트 타입의 남성 입니다."
        elif "여름 쿨 라이트" in result_response:
            personal_type = "저는 여름 쿨 라이트 타입의 남성 입니다."
        elif "여름 쿨 뮤트" in result_response:
            personal_type = "저는 여름 쿨 뮤트 타입의 남성 입니다."
        elif "가을 웜 뮤트" in result_response:
            personal_type = "저는 가을 웜 뮤트 타입의 남성 입니다."
        elif "가을 웜 다크" in result_response:
            personal_type = "저는 가을 웜 다크 타입의 남성 입니다."
        elif "겨울 쿨 브라이트" in result_response:
            personal_type = "저는 겨울 쿨 브라이트 타입의 남성 입니다."
        elif "겨울 쿨 다크" in result_response:
            personal_type = "저는 겨울 쿨 다크 타입의 남성 입니다."
        else:
            personal_type = None

    elif gender == "female":
        if "봄 웜 브라이트" in result_response:
            personal_type = "저는 봄 웜 브라이트 타입의 여성 입니다."
        elif "봄 웜 라이트" in result_response:
            personal_type = "저는 봄 웜 라이트 타입의 여성 입니다."
        elif "여름 쿨 라이트" in result_response:
            personal_type = "저는 여름 쿨 라이트 타입의 여성 입니다."
        elif "여름 쿨 뮤트" in result_response:
            personal_type = "저는 여름 쿨 뮤트 타입의 여성 입니다."
        elif "가을 웜 뮤트" in result_response:
            personal_type = "저는 가을 웜 뮤트 타입의 여성 입니다."
        elif "가을 웜 다크" in result_response:
            personal_type = "저는 가을 웜 다크 타입의 여성 입니다."
        elif "겨울 쿨 브라이트" in result_response:
            personal_type = "저는 겨울 쿨 브라이트 타입의 여성 입니다."
        elif "겨울 쿨 다크" in result_response:
            personal_type = "저는 겨울 쿨 다크 타입의 여성 입니다."
        else:
            personal_type = None

    return personal_type


def print_result():
    if result_response != None:
        return result_response


def male_button():
    global gender
    if gender is None:
        gender = "male"
        return "남자를 선택하셨습니다. 아래에서 사진을 업로드하거나 촬영해 주세요."
    return "이미 남자를 선택하셨습니다."

def female_button():
    global gender
    if gender is None:
        gender = "female"
        return "여자를 선택하셨습니다. 아래에서 사진을 업로드하거나 촬영해 주세요."
    return "이미 여자를 선택하셨습니다."


# 기존 Chroma 데이터베이스 디렉토리
save_directory = "./chroma_db"

# 임베딩 모델 생성
model = langchain_retriever_utils.embedding_model()

# 기존 Chroma 데이터베이스 로드 또는 새로 생성
if os.path.exists(save_directory):
    db = langchain_retriever_utils.load_existing_chroma(save_directory, model)
else:
    # 문서 업로드
    loader = langchain_retriever_utils.docs_load("./data/RGB_results.pdf")

    # 문서 분할
    chunk = langchain_retriever_utils.rc_text_split(loader)
    print(chunk)

    # 문서 임베딩
    db = langchain_retriever_utils.document_embedding(chunk, model, save_directory)

# 채팅에 사용할 거대언어모델(LLM) 선택
llm = langchain_retriever_utils.chat_llm()

gender = None

# Gradio 앱 설정
with gr.Blocks() as demo:
    gr.Markdown("# ToneMate")

    gr.Markdown("### 성별을 선택하세요")
    with gr.Row():
        btn1 = gr.Button("남자")
        btn2 = gr.Button("여자")

    output = gr.Textbox(label="안내")
    btn1.click(fn=male_button, inputs=[], outputs=output)
    btn2.click(fn=female_button, inputs=[], outputs=output)

    # 웹캠 섹션
    gr.Markdown("### 상반신이 화면에 나오도록 사진을 촬영하거나 업로드해주세요")
    webcam = gr.Interface(process_image, gr.Image(), "image")

    gr.Markdown("### 이미지 결과가 나온 뒤에 '진단하기'버튼을 눌러주세요.")
    result_button = gr.Button("진단하기")
    output_text = gr.Textbox(label="퍼스널 컬러 진단 내용", lines=15)
    result_button.click(print_result, inputs=[], outputs=output_text)

    # 챗봇 섹션
    gr.Markdown("## 문서 기반 질문과 답변")
    chatbot_display = gr.Chatbot(label="퍼스널 컬러 상담", type="messages")
    user_input = gr.Textbox(label="질문을 입력하세요", placeholder="질문을 입력하고 버튼을 눌러주세요.")
    submit_button = gr.Button("질문하기")

    # 상태 저장
    state = gr.State([])


    # 질문 처리 함수
    def handle_qa(state, user_input):
        if isinstance(state, str):
            state = []

        content = result_response
        personal_type = color_type(result_response, gender)
        response = langchain_retriever_utils.chat_qna(llm, db, user_input, content, personal_type)

        profile_1 = 'https://lh3.googleusercontent.com/fife/ALs6j_EqXIVckhgZ2o5OHlF28pORP2VOCi-2dsX5CN5heWmQgbCx-z9Na0IV3BJJbWmk1RkYKdrzyya_f0L1WG0g5DQJp_pEeyMLVyZy_KtfYLDQN9RWhiY9i9cgyC6bNEBLT3Xohjj0KK4DFNCjyDVB_iF_8QaUaHqgXihwSi3O7MfDptLeMVKPERXRxgSpSXQI6cNlf0R6WQ8ef0u1OE7Xi2V6FUlyLAepjOtO7Yrh1om9VNfvadWRYwok44m97o8Nik-3snQjmePP2e0Z1Wbsi5fW6l-_oovb0dSBmfqKuuPY1QeiDia3upd7CI6W-IoyuMs1K8RJ5N_3mfUBHHd-mrceS1iA0ULdxtpyv2X1eK1sgFbpnLC3zQonV3KqVyabNcNifxM5ADj1SZE7O_b5gsYo1l9bDmtvDM3AME9o2wlT_vG6Ws9W7sO7gpPpWjaIq52yYPZ_5W3Lu1-ubFWaw4Vr-T9VFdrK4yryGhKaNqtHdIAv0VG-QUZXAqJRdYRei-kZYzZ_sa614zjxR3Bvs61WaP88G--T528YrPjp8zOPCvKgThYrlZWZ7Y-wLsFjZ4kp2KqXr133LDJ48ic6HWQoZXUpLfrOKedxZQcXQ1T_meT7FIrpE_5VtAKdh6wInBuXn9Rt2q6_-zx9fKix87IuHQvjOoKCBjw_NvEm6ZUA0RtCvG3Smp2cjcyu6xJ9W8xa1EMJEHiPBx0ITjdRQciqOepIbMcvkJAgH6d7NcPG9b8DaUOQUyyeuHkBImq9CAOAsKhTviCz-yTadumgb3XJc_nSbwgeJcSV6a9SRL8tt_rkaINtW_oMAYU1ilX6Z16xnWZAfd0HlWj2v7HG0y705ihQmW7aF1DwnxrajGrMn9WJJkolHdkwSJQ9JjNcrKzQ4EViQcCMDpNyHQRdtgxLh5o-ux1A4td_JdrVHm2VeFPIjncc94Br2rCwxwKMplmxgWPhzjvhTkQ3gl5qRoLEmX0cv3p7e8CiK8oE9lxYpJBK9A3uJKoISBA96aoMXdHxD0sUdx4K5Pki83RPb61Wf8JeRUpEgqIX0327In4cisvkjxsB_uO2RUn9nSAE9TVZC25O6YDyIzodCQRnLA7yvxLksd3OIq7s6KPENBw-DosehZpf4pcfwJiA-8AwTfX2Ul5pQAW8LA1gb9QuC1b0Btcq69ynENLGRi7E7wlqHEpGF8RWHY3h1ECWwYeQ6kpTRfHIZ2bnrxWP-0tb7J-Z-ijiRtEaxDOib2oPhXIDqBmZ6RtW2kYOLjiLYte7vpqV4bCZP11d9zfdRGEdR2gYN7FkXSdKzgE70YQxaLItpX4XwIz4XfbOlWg_iYu0DdfeIXwaLclDyrbaVuCp5GQBvnXfaREoNO_qDze4KWVWCqEtqcpXrJa89swAMgTQv4SE_3bfI-6ncDI-36_6VKaKm_1wQ3tpRmeHJcmyUlwq8JzOn_uI8i0qUzBmEf2zoqXtjWSkKnQqji1PRIhVB1Wf7X8nUhiVN-8SnPBVj4YvYiZNeMyOqLr2A5YxLiBxcI7Osu5m9N6IrQsVY2qCCMBwu2pIiqvNjL35pJbYIzPYIW1Q4ucStGlSGuIwg3rrjDxnmAB4OTKHEPMNR2hoRpm99vzrcgyK8FWbFasz_rGWOIBVbWBDPAgLDOzRvhxF6H-Pn_BUkj56zmTlEkbqluo7B5e8WYD2_Yu7EjnZHxI26V_RPu6g_6vAJ27JiHuxeam0xQjTsB1KI1uvyFb1pPgU04buO1VnwxwDmdA=w2926-h1646'
        profile_html = f"<img src='{profile_1}' style='width:65px;height:65px;border-radius: 50%;margin-right: 10px;' />"
        state.append({"role": "user", "content": user_input})
        state.append({"role": "assistant", "content": profile_html + "\n\n" + response})
        return state, state


    submit_button.click(handle_qa, inputs=[state, user_input], outputs=[chatbot_display, state])

# 앱 실행
if __name__ == "__main__":
    demo.launch(share=True)