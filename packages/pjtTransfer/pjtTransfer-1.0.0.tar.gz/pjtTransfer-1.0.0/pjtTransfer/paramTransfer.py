import os
import pickle
from traceback import print_exc
import json
# 获取当前模块的路径
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
path = MODULE_PATH + "\pjtTransferDictionary.pkl"
file = open(path, 'rb')  # 以二进制读模式（rb）打开pkl文件
pjtTransferDictionary = pickle.load(file)  # 读取存储的pickle文件

df_pjt_damage_standards = pjtTransferDictionary["df_pjt_damage_standards"]
model_productId_dic = pjtTransferDictionary["model_productId_dic"]
id_model_dic = pjtTransferDictionary["id_model_dic"]
model_id_dic = pjtTransferDictionary["model_id_dic"]
dic_transfer = pjtTransferDictionary["dic_transfer"]
standardsCode_chxStandards_dic = pjtTransferDictionary["standardsCode_chxStandards_dic"]
# print(standardsCode_chxStandards_dic)
# print(len(standardsCode_chxStandards_dic))
dic_productId_allJson = pjtTransferDictionary["dic_productId_allJson"]
# print(len(dic_productId_allJson))

class paramTransfer:
    df_pjt_damage_standards = df_pjt_damage_standards
    model_productId_dic = model_productId_dic
    id_model_dic = id_model_dic
    model_id_dic = model_id_dic
    dic_transfer = dic_transfer
    standardsCode_chxStandards_dic = standardsCode_chxStandards_dic
    dic_productId_allJson = dic_productId_allJson
    def __init__(self):
        self.dic_productId_allJson = dic_productId_allJson
        self.model_productId_dic = model_productId_dic
        self.id_model_dic = id_model_dic
        self.model_id_dic = model_id_dic
        self.dic_transfer = dic_transfer
        self.standardsCode_chxStandards_dic = standardsCode_chxStandards_dic
        self.df_pjt_damage_standards = df_pjt_damage_standards

    def get_properties_info(self,productId,data,zzt_desc_code_dic):
        netWork = data["netWork"]
        purchaseChannel = data["purchaseChannel"]
        color = data["color"]
        if(purchaseChannel == "国行"):
            purchaseChannel = "大陆国行"
        post_id_li = []
        post_CN_li = []

        warranty_period = data["warranty_period"]
        if(data["ram"] !="" and data["ram"] != None):
            ram_storage = data["ram"]+"+"+data["storage"]
            item_data = [purchaseChannel, color, ram_storage, warranty_period, netWork]

        else:
            ram_storage = data["storage"]
            item_data = [ram_storage, purchaseChannel, color, warranty_period, netWork]
        # print(item_data)
        try:
            all_json = json.loads(self.get_jsdataByProductId(productId))
            # print(all_json)
            data = all_json["data"]
        except TypeError as e:
            return [],[]

        #选择物品信息
        item_infos = data[0]["properties"]
        # print(item_infos)
        # print(len(item_infos))
        for item_info in item_infos:
            name_ = item_info["name"]
            pricePropertyValues = item_info["pricePropertyValues"]
            df_pjt_damage_standards_properties = self.df_pjt_damage_standards[
                (self.df_pjt_damage_standards["sdandards_Level_1"] == "物品信息") & (
                            self.df_pjt_damage_standards["sdandards_Level_2"] == f"{name_}")]
            dic_pjt_properties = {}
            dic_pjt_properties_reverse = {}
            for i in range(df_pjt_damage_standards_properties.shape[0]):
                pjt_properties_id = df_pjt_damage_standards_properties["id"].iloc[i]
                pjt_warranty_period_CN = \
                df_pjt_damage_standards_properties["sdandards_Level_3"].iloc[i]
                dic_pjt_properties[pjt_warranty_period_CN] = pjt_properties_id
                dic_pjt_properties_reverse[pjt_properties_id] = pjt_warranty_period_CN
            # print(dic_pjt_properties)
            flag_ = True
            for pricePropertyValue in pricePropertyValues:
                # print(damageInfor_CN_li, pricePropertyValue["value"])

                if(pricePropertyValue["value"] in item_data):
                    # print(damageInfor_CN_li,pricePropertyValue["value"])
                    flag_ = False
                    pricePropertyValue["isPreferred"] = True
                    post_CN_li.append(pricePropertyValue["value"])
                    post_id_li.append(dic_pjt_properties[pricePropertyValue["value"]])
                    break
                else:
                    pricePropertyValue["isPreferred"] = False
            if(flag_):
                pricePropertyValues[0]["isPreferred"] = True
                post_CN_li.append(pricePropertyValues[0]["value"])
                post_id_li.append(dic_pjt_properties[pricePropertyValues[0]["value"]])


        #选择成色情况
        damageInfor_CN_li = []
        pjt_damage_id_li = zzt_desc_code_dic.values()
        for i in range(self.df_pjt_damage_standards.shape[0]):
            if(self.df_pjt_damage_standards["id"].iloc[i] in pjt_damage_id_li):
                damageInfor_CN_li.append(self.df_pjt_damage_standards["sdandards_Level_3"].iloc[i])
        quality_infos = data[1]["properties"]
        # print(quality_infos)
        # print(len(quality_infos))
        for quality_info in quality_infos:
            name_ = quality_info["name"]
            pricePropertyValues = quality_info["pricePropertyValues"]
            df_pjt_damage_standards_properties = self.df_pjt_damage_standards[
                (self.df_pjt_damage_standards["sdandards_Level_1"] == "成色情况") & (
                            self.df_pjt_damage_standards["sdandards_Level_2"] == f"{name_}")]
            dic_pjt_properties = {}
            dic_pjt_properties_reverse = {}
            for i in range(df_pjt_damage_standards_properties.shape[0]):
                pjt_properties_id = df_pjt_damage_standards_properties["id"].iloc[i]
                pjt_warranty_period_CN = \
                df_pjt_damage_standards_properties["sdandards_Level_3"].iloc[i]
                dic_pjt_properties[pjt_warranty_period_CN] = pjt_properties_id
                dic_pjt_properties_reverse[pjt_properties_id] = pjt_warranty_period_CN
            # print(dic_pjt_properties)
            flag_ = True
            for pricePropertyValue in pricePropertyValues:
                # print(damageInfor_CN_li, pricePropertyValue["value"])
                if(pricePropertyValue["value"] in damageInfor_CN_li):
                    # print(damageInfor_CN_li,pricePropertyValue["value"])
                    flag_ = False
                    pricePropertyValue["isPreferred"] = True
                    post_CN_li.append(pricePropertyValue["value"])
                    post_id_li.append(dic_pjt_properties[pricePropertyValue["value"]])
                    break
                else:
                    pricePropertyValue["isPreferred"] = False
            if(flag_):
                pricePropertyValues[0]["isPreferred"] = True
                post_CN_li.append(pricePropertyValues[0]["value"])
                post_id_li.append(dic_pjt_properties[pricePropertyValues[0]["value"]])
            # print(quality_info)
        #选择功能情况
        function_infos = data[2]["properties"]
        # print(function_infos)
        # print(len(function_infos))
        for function_info in function_infos:
            name_ = function_info["name"]
            pricePropertyValues = function_info["pricePropertyValues"]
            df_pjt_damage_standards_properties = self.df_pjt_damage_standards[
                (self.df_pjt_damage_standards["sdandards_Level_1"] == "功能情况") & (
                            self.df_pjt_damage_standards["sdandards_Level_2"] == f"{name_}")]
            dic_pjt_properties = {}
            dic_pjt_properties_reverse = {}
            for i in range(df_pjt_damage_standards_properties.shape[0]):
                pjt_properties_id = df_pjt_damage_standards_properties["id"].iloc[i]
                pjt_warranty_period_CN = \
                df_pjt_damage_standards_properties["sdandards_Level_3"].iloc[i]
                dic_pjt_properties[pjt_warranty_period_CN] = pjt_properties_id
                dic_pjt_properties_reverse[pjt_properties_id] = pjt_warranty_period_CN
            # print(dic_pjt_properties)
            flag_ = True
            for pricePropertyValue in pricePropertyValues:
                # print(damageInfor_CN_li, pricePropertyValue["value"])
                if(pricePropertyValue["value"] in damageInfor_CN_li):
                    # print(damageInfor_CN_li,pricePropertyValue["value"])
                    flag_ = False
                    pricePropertyValue["isPreferred"] = True
                    post_CN_li.append(pricePropertyValue["value"])
                    post_id_li.append(dic_pjt_properties[pricePropertyValue["value"]])
                    break
                else:
                    pricePropertyValue["isPreferred"] = False
            if(flag_):
                pricePropertyValues[0]["isPreferred"] = True
                # print(pricePropertyValues[0])
                post_CN_li.append(pricePropertyValues[0]["value"])
                try:
                    post_id_li.append(dic_pjt_properties[pricePropertyValues[0]["value"]])
                except KeyError as e:
                    post_id_li.append(pricePropertyValues[0]["id"])
                # print(dic_pjt_properties)
            # print(function_info)

        all_json["data"][0] = item_infos
        all_json["data"][1] = quality_infos
        all_json["data"][2] = function_infos
        # print(post_CN_li)
        # print(post_id_li)
        # print(all_json)
        for i in range(len(post_id_li)):
            if(post_id_li[i] == 10203):
                post_id_li[i] = 9625
                post_CN_li[i] = "已激活，可还原"
            elif(post_id_li[i] == 20267):
                post_id_li[i] = 20268
                post_CN_li[i] = "90%＜电池健康度≤99%"
            elif(post_id_li[i] == 2124):
                post_id_li[i] = 2125
                post_CN_li[i] = "外壳完美"
        return post_id_li,post_CN_li

    def get_jsdataByProductId(self,ProductId):
        try:
            dic_productId_allJson = self.dic_productId_allJson
            return dic_productId_allJson[str(ProductId)]
        except Exception as e:
            print(f"paramTransfer.py 196行 pjt_inspection不存在product_id:{ProductId}")
            # print_exc()
            # if (ProductId != None):
            #     with open("cralwer/data/lacked_productId.csv", mode="a+", encoding="utf-8") as info_csv:
            #         info_csv_obj = csv.writer(info_csv, dialect='excel')
            #         info_csv_obj.writerow([ProductId])

    def verifyCHXdesc(self,desc_CN_dic):
        standardsCode_li = []
        for q_level_1,q_level_2 in desc_CN_dic.items():
            main_desc_li = q_level_2.split("|")
            for desc in main_desc_li:
                try:
                    standardsCode = self.standardsCode_chxStandards_dic[desc]
                    standardsCode_li.append(standardsCode)
                except KeyError as e:
                    pass
                    continue
                    # if (desc != None):
                    #     with open("cralwer/data/lacked_desc.csv", mode="a+", encoding="utf-8") as info_csv:
                    #         info_csv_obj = csv.writer(info_csv, dialect='excel')
                    #         info_csv_obj.writerow([desc])
                    #         continue

        # print(desc_CN_dic)
        # print(standardsCode_li)
        return standardsCode_li

    def returnSearchPriceParam(self, data):
        try:
            data["damageInfor"] = json.loads(data["damageInfor"])
        except Exception as e:
            pass

        if(type(data["model"]) != int):
            try:
                data["model"] = self.model_id_dic[data["model"]]
            except KeyError as e:
                pass

        try:
            data["damageInfor"] = self.createDamageInfor(data["damageInfor"])
        except Exception as e:
            pass
        try:
            damageInfor_li = data["damageInfor"]
            model = data["model"]

            zzt_desc_code_dic = {}
            try:
                for code in damageInfor_li:

                    zzt_desc_code_dic[code] = self.dic_transfer[code]
            except TypeError as e:
                pass
            post_id_li, post_CN_li = self.get_properties_info(model, data, zzt_desc_code_dic)

            return {
                    "productId": model,
                    "pjt_post_data": {"post_id_li": post_id_li, "post_CN_li": post_CN_li},}
        except Exception as e:
            print_exc()

    def createDamageInfor(self,damage):
        damage_info = self.verifyCHXdesc(damage)
        return damage_info
if __name__ == '__main__':
    #安卓手机数据传入 例
    data =   {
        "model": "荣耀 X20",
        "netWork":"全网通",
        "purchaseChannel":"国行",
        "color": "银色",
        "ram": "6G",
        "storage": "256G",
        "warranty_period":"",
        "damageInfor":
        {"使用功能": "电池健康度100%|后摄像头拍照有斑|光线/距离感应异常", "屏幕显示": "显示明显老化", "机身外观": "外壳缺失/裂缝/孔变形/翘起/刻字|屏幕硬划痕（≥10毫米）"}
    }
    trans = paramTransfer()
    result = trans.returnSearchPriceParam(data)
    print(result)

    #苹果手机数据传入 例
    data =   {
        "model": "iPhone 8 Plus",
        "netWork":"全网通",
        "purchaseChannel":"国行",
        "color": "黑色钛金属",
        "ram": "6G",
        "storage": "512G",
        "warranty_period":"",
        "damageInfor":
        {"屏幕外观": "屏有硬划痕（≥10毫米）", "边框背板": "外壳明显磕碰/掉漆（≥3毫米），或镜片破损"}
    }
    trans = paramTransfer()
    result = trans.returnSearchPriceParam(data)
    print(result)



