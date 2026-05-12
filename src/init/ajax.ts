import { AjaxService } from "~/features/core/ajaxService"
import { API_BASE_URL } from '~/config';

export const ajaxService = new AjaxService(API_BASE_URL);
